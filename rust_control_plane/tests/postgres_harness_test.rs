mod support;

#[tokio::test]
async fn postgres_harness_applies_messaging_migrations() {
    let pool = support::postgres::test_pool()
        .await
        .expect("dedicated PostgreSQL test harness must initialize");

    let migrations_table: Option<String> =
        sqlx::query_scalar("SELECT to_regclass('_sqlx_migrations')::text")
            .fetch_one(&pool)
            .await
            .expect("migration metadata query must succeed");

    assert_eq!(migrations_table.as_deref(), Some("_sqlx_migrations"));
}
