<template>
  <div>
    <v-breadcrumbs :items="breadcrumbs">
      <template v-slot:divider>
        <v-icon>mdi-chevron-right</v-icon>
      </template>
    </v-breadcrumbs>

    <v-container>
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

        <v-data-table v-if="tables" disable-pagination hide-default-footer :headers="headers" :items="tables" :search="search" no-data-text="Data not found...">
          <template v-slot:[`item.name`]="{item}" >
            <router-link :to="{ name: 'Table', params: { tableName: item.name }}">{{ item.name }}</router-link>
          </template>
          <template v-slot:[`item.total_bytes`]="{item}" >
            {{(item.total_bytes / 1024 / 1024).toFixed(3)}} MB
          </template>
        </v-data-table>

        <v-data-table
          v-else
          hide-default-header
          hide-default-footer
          loading
          loading-text="Loading... Please wait"
        />
      </v-card>
    </v-container>
  </div>
</template>

<script>
import Clickhouse from '@/api/clickhouse.js'

export default {
  name: 'Tables',
  components: {},
  data: () => ({
    breadcrumbs: [
      { text: 'Home', exact: true, disabled: false, to: { name: 'Home' } },
      { text: 'Tables', exact: true, disabled: false, to: { name: 'Tables' } }
    ],
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
  mounted() {
    Clickhouse.listTables(res => {
      this.tables = res
    })
  }
}
</script>
