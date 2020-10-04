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
          Data Sources
          <v-spacer></v-spacer>
          <v-text-field
            v-model="search"
            append-icon="mdi-magnify"
            label="Search"
            single-line
            hide-details
          ></v-text-field>
        </v-card-title>

        <v-data-table v-if="sources" disable-pagination hide-default-footer :headers="headers" :items="sources" :search="search" no-data-text="Data not found...">
          <!-- <template v-slot:[`item.name`]="{item}" >
            <router-link :to="{ name: 'Table', params: { tableName: item.name }}">{{ item.name }}</router-link>
          </template> -->
          <template v-slot:[`item.total_bytes`]="{item}" >
            {{(item.total_bytes / 1024 / 1024).toFixed(3)}} MB
          </template>
          <template v-slot:[`item.newest_table_create_at`]="{item}" >
            {{createAtFormat(item.newest_table_create_at)}}
          </template>
          <template v-slot:[`item.oldest_table_create_at`]="{item}" >
            {{createAtFormat(item.oldest_table_create_at)}}
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
  name: 'Sources',
  data: () => ({
    breadcrumbs: [
      { text: 'Home', exact: true, disabled: false, to: { name: 'Home' } },
      { text: 'Sources', exact: true, disabled: false, to: { name: 'Sources' } }
    ],

    headers: [
      { text: 'Source ID', sortable: true, value: 'source_id', align: 'start' },
      { text: 'Table Count', sortable: true, value: 'table_count' },
      { text: 'Total Row Count', sortable: true, value: 'total_rows' },
      { text: 'Total Size', sortable: true, value: 'total_bytes' },
      { text: 'Newest Table Created At', sortable: true, value: 'newest_table_create_at' },
      { text: 'Oldest Table Created At', sortable: true, value: 'oldest_table_create_at' }
    ],
    sources: null,
    // tables: null,
    search: ''
  }),

  mounted() {
    Clickhouse.listSources(res => {
      res.forEach(r => {
        r.newest_table_create_at = new Date(r.newest_table_create_at).getTime()
        r.oldest_table_create_at = new Date(r.oldest_table_create_at).getTime()
      })
      this.sources = res
    },
    err => {
      console.log(err)
    })
  },
  methods: {
    createAtFormat(createAt) {
      var moment = require('moment')
      return moment(new Date(createAt)).format('YYYY-MM-DD HH:mm:ss')
    }
  }
}
</script>

<style>

</style>
