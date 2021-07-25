FROM metabase/metabase:v0.40.1 as metabase-with-clickhouse

# /plugins/ is default path to plugins dir.
ADD plugins/*.jar /plugins/

ENV JAVA_OPTS="$JAVA_OPTS -Duser.timezone=$TZ"
