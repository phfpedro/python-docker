import os

from pyspark.sql import SparkSession, functions as F
from delta import configure_spark_with_delta_pip

LAKE = "s3a://datalake"

ENDPOINT = os.environ.get("MINIO_ENDPOINT", "http://minio:9000")
KEY = os.environ.get("AWS_ACCESS_KEY_ID", "minioadmin")
SECRET = os.environ.get("AWS_SECRET_ACCESS_KEY", "minioadmin")


def get_spark(app):
    builder = (
        SparkSession.builder
        .appName(app)
        .master("local[2]")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.local.dir", "/tmp/spark-local")
        .config("spark.eventLog.enabled", "false")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.default.parallelism", "2")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog"
        )
        .config("spark.hadoop.fs.s3a.endpoint", ENDPOINT)
        .config("spark.hadoop.fs.s3a.access.key", KEY)
        .config("spark.hadoop.fs.s3a.secret.key", SECRET)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
    )

    return configure_spark_with_delta_pip(
        builder,
        extra_packages=[
            "org.apache.hadoop:hadoop-aws:3.3.4",
            "com.amazonaws:aws-java-sdk-bundle:1.12.262"
        ]
    ).getOrCreate()


def run_bronze():
    spark = get_spark("bronze")

    try:
        (
            spark.read
            .option("header", "true")
            .csv(f"{LAKE}/landing/vendas")
            .withColumn("_ingest_ts", F.current_timestamp())
            .withColumn("_source_file", F.input_file_name())
            .write
            .format("delta")
            .mode("overwrite")
            .save(f"{LAKE}/bronze/vendas")
        )
    finally:
        spark.stop()


def run_silver():
    spark = get_spark("silver")

    try:
        b = spark.read.format("delta").load(f"{LAKE}/bronze/vendas")

        limpo = (
            b
            .withColumn("produto", F.lower(F.trim(F.col("produto"))))
            .withColumn(
                "valor",
                F.regexp_replace(F.col("valor"), ",", ".").cast("double")
            )
            .withColumn("quantidade", F.col("quantidade").cast("int"))
            .withColumn("data", F.to_date(F.col("data"), "dd/MM/yyyy"))
        )

        valido = (
            F.col("produto").isNotNull()
            & (F.col("produto") != "")
            & F.col("valor").isNotNull()
            & (F.col("valor") > 0)
            & F.col("data").isNotNull()
        )

        (
            limpo
            .filter(valido)
            .dropDuplicates(["venda_id", "produto", "loja", "valor", "data"])
            .write
            .format("delta")
            .mode("overwrite")
            .save(f"{LAKE}/silver/vendas")
        )

        (
            limpo
            .filter(~valido)
            .write
            .format("delta")
            .mode("overwrite")
            .save(f"{LAKE}/silver/vendas_quarentena")
        )

        total = limpo.count()

        ok = (
            spark.read
            .format("delta")
            .load(f"{LAKE}/silver/vendas")
            .count()
        )

        taxa_qualidade = ok / total if total > 0 else 0

    finally:
        spark.stop()

    assert taxa_qualidade > 0.80, f"Qualidade abaixo do limite: {taxa_qualidade:.1%}"


def run_gold():
    spark = get_spark("gold")

    try:
        silver = spark.read.format("delta").load(f"{LAKE}/silver/vendas")

        fato = silver.select(
            "venda_id",
            "data",
            "produto",
            "loja",
            "quantidade",
            F.col("valor").alias("valor_unitario"),
            (F.col("valor") * F.col("quantidade")).alias("valor_total")
        )

        (
            fato.write
            .format("delta")
            .mode("overwrite")
            .save(f"{LAKE}/gold/fato_vendas")
        )

        (
            (
                fato
                .withColumn("mes", F.date_format("data", "yyyy-MM"))
                .groupBy("loja", "mes")
                .agg(
                    F.round(F.sum("valor_total"), 2).alias("faturamento"),
                    F.sum("quantidade").alias("itens_vendidos"),
                    F.countDistinct("venda_id").alias("num_vendas")
                )
                .write
                .format("delta")
                .mode("overwrite")
                .save(f"{LAKE}/gold/faturamento_por_loja_mes")
            )
        )

    finally:
        spark.stop()