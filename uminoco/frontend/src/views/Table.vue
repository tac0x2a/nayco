<template>
  <div>
    <v-breadcrumbs :items="breadcrumbs">
      <template v-slot:divider>
        <v-icon>mdi-chevron-right</v-icon>
      </template>
    </v-breadcrumbs>

    <div v-if="tableData">
      <v-card class="mx-auto" max-width="auto" outlined tile>
        <v-card-text>
          <div>Table</div>
          <p class="display-1 text--primary">{{tableData.name}}</p>
        </v-card-text>
      </v-card>

      <v-container class="grey lighten-3">
        <v-row no-gutters>
          <v-col key="1" cols="12" sm="4">
            <v-card class="pa-2" outlined tile><v-card-text><div>Rows</div><p class="headline mb-1">{{tableData.total_rows}}</p></v-card-text></v-card>
          </v-col>
          <v-col key="2" cols="12" sm="4">
            <v-card class="pa-2" outlined tile><v-card-text><div>Bytes[MB]</div><p class="headline mb-1">{{(tableData.total_bytes/1024.0/1024.0).toFixed(4)}}</p></v-card-text></v-card>
          </v-col>
          <v-col key="3" cols="12" sm="4">
            <v-card class="pa-2" outlined tile><v-card-text><div>Compression Ratio</div><div class="headline mb-1">{{(tableData.compression_ratio * 100).toFixed(2)}} %</div></v-card-text></v-card>
          </v-col>
        </v-row>
      </v-container>

      <div>
        <v-card>
          <v-card-title>
            Columns
            <v-spacer></v-spacer>
            <v-text-field
              v-model="search"
              append-icon="mdi-magnify"
              label="Search"
              single-line
              hide-details
            ></v-text-field>
          </v-card-title>

          <v-data-table dense disable-pagination hide-default-footer :headers="columnsHeader" :items="tableData.columns" :search="search" no-data-text="Data not found...">
            <template v-slot:[`item.compression_ratio`]="{item}" >
              {{(item.compression_ratio * 100).toFixed(2)}} %
            </template>

            <template v-slot:[`item.data_uncompressed_bytes`]="{item}" >
              {{(item.data_uncompressed_bytes/1024.0).toFixed(2)}}
            </template>
            <template v-slot:[`item.data_compressed_bytes`]="{item}" >
              {{(item.data_compressed_bytes/1024.0).toFixed(2)}}
            </template>
            <template v-slot:[`item.marks_bytes`]="{item}" >
              {{(item.marks_bytes/1024.0).toFixed(2)}}
            </template>

          </v-data-table>
        </v-card>
      </div>

    </div>
    <div v-else>
      <v-data-table
        hide-default-header
        hide-default-footer
        loading
        loading-text="Loading... Please wait"
      />
    </div>
  </div>
</template>

<script>
import Clickhouse from '@/api/clickhouse.js'

export default {

  name: 'Table',
  components: {},
  data: () => ({
    breadcrumbs: [
      { text: 'Home', exact: true, disabled: false, to: { name: 'Home' } },
      { text: 'Tables', exact: true, disabled: false, to: { name: 'Tables' } }
    ],
    tableData: null,
    search: '',
    columnsHeader: [
      { text: 'Name', sortable: true, value: 'name' },
      { text: 'Type', sortable: true, value: 'type' },
      { text: 'Size [KB]', sortable: true, value: 'data_compressed_bytes' },
      { text: 'Compression Ratio', sortable: true, value: 'compression_ratio' },
      { text: 'Marks Size [KB]', sortable: true, value: 'marks_bytes' },
      { text: 'Original Size [KB]', sortable: true, value: 'data_uncompressed_bytes' },
      { text: 'Position', sortable: true, value: 'position' }
    ]
  }),
  props: ['tableName'],
  watch: {
    tableName: {
      handler() {
        this.breadcrumbs.push({ text: this.tableName, disabled: true })

        Clickhouse.tableDetail(this.tableName, res => {
          this.tableData = res
        })
      },
      immediate: true
    }
  }
}
</script>
