<template>
  <div>
    <v-card>
      <v-card-title>
        Tables
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
        ></v-text-field>
      </v-card-title>

      <v-data-table
        v-if="tables"
        :headers="headers"
        :items="tables"
        :search="search" />
      <v-data-table
        v-else
        hide-default-header
        hide-default-footer
        loading loading-text="Loading... Please wait" />
    </v-card>
  </div>
</template>

<script>
import Clickhouse from '@/api/clickhouse.js'

export default {
  name: 'Table',
  components: {},
  data: () => ({
    headers: [
      { text: 'Table Name', sortable: true, value: 'name', align: 'start' },
      { text: 'Row Count', sortable: true, value: 'total_rows' },
      { text: 'Table size [Byte]', sortable: true, value: 'total_bytes' },
      { text: 'Engine', sortable: true, value: 'engine' }
    ],
    tables: null,
    // tables: null,
    search: ''
  }),
  mounted () {
    Clickhouse.listTables(res => {
      this.tables = res
    })
  }
}
</script>
