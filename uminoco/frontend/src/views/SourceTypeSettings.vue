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
          {{this.sourceId + ' - Column and Types'}}
          <v-spacer></v-spacer>
          <v-text-field
            v-model="search"
            append-icon="mdi-magnify"
            label="Search"
            single-line
            hide-details
          ></v-text-field>
        </v-card-title>
        <v-data-table v-if="tableData" :headers="headers" :items="tableData" :search="search" no-data-text="Data not found...">
          <template v-slot:[`item.__corrected_type__`]="{item}" >
            <v-text-field v-model="correctedTypes[item.__column_name__]"
            placeholder="Auto Detect"
            dense
            :clearable=true
          ></v-text-field>
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

    <v-container>
      <v-row>
        <v-col class="text-center" cols="12" sm="10"></v-col> <!-- dummy -->
        <v-col class="text-center" cols="12" sm="2">
          <v-btn color="success" @click=applyCorrectTypes() :disabled=btnDisabled>Apply</v-btn>
        </v-col>
      </v-row>
    </v-container>

    <!-- APPLY RESULT -->
    <v-snackbar
      v-model="snackbar"
      :timeout=2000
    >
      Apply Completed!!
      <template v-slot:action="{ attrs }">
        <v-btn
          color="blue"
          text
          v-bind="attrs"
          @click="snackbar = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
import Clickhouse from '@/api/clickhouse.js'

export default {
  name: 'Sources',
  props: ['sourceId'],
  data: () => ({
    breadcrumbs: [
      { text: 'Home', exact: true, disabled: false, to: { name: 'Home' } },
      { text: 'Sources', exact: true, disabled: false, to: { name: 'Sources' } }
    ],
    tableData: null,
    headers: null,
    search: '',
    sourceColumns: null,
    specifiedTypes: null,
    tableNames: null,
    correctedTypes: {},
    btnDisabled: false,
    snackbar: false,
    snackbarMessage: ''
  }),
  mounted() {
    Clickhouse.sourceSpecifiedTypes(this.sourceId, res => {
      this.sourceColumns = res.columns
      this.specifiedTypes = res.specified_types
      this.tableNames = res.table_names

      // Header
      const headers = this.tableNames.map(name => {
        return { text: name, sortable: true, value: name }
      })
      this.headers = [
        { text: 'Column', sortable: true, value: '__column_name__' },
        { text: 'Corrected Type', sortable: true, value: '__corrected_type__' }
      ].concat(headers)

      // tableData
      this.tableData = Object.keys(this.sourceColumns).map(columnName => {
        const column = this.sourceColumns[columnName]
        const record = column.types
        record.__column_name__ = columnName
        record.__corrected_type__ = column.specified_type
        record.__selectable_types__ = column.selectable_types
        return record
      })

      Object.keys(this.sourceColumns).forEach(columnName => {
        const column = this.sourceColumns[columnName]
        this.correctedTypes[columnName] = column.specified_type
      })
    },
    err => {
      console.log(err)
    })
  },
  methods: {
    createAtFormat(createAt) {
      var moment = require('moment')
      return moment(new Date(createAt)).format('YYYY-MM-DD HH:mm:ss')
    },
    applyCorrectTypes() {
      this.btnDisabled = true

      const postData = {}
      Object.keys(this.correctedTypes).forEach(k => {
        if (this.correctedTypes[k] === null) return
        if (this.correctedTypes[k].length <= 0) return
        postData[k] = this.correctedTypes[k]
      })

      Clickhouse.updateSourceTypes(this.sourceId, postData, res => {
        this.snackbarMessage = 'Apply Success!!'
        this.snackbar = true
        this.btnDisabled = false
      },
      err => {
        this.snackbarMessage = err.message
        this.snackbar = true
        this.btnDisabled = false
        console.log(err)
      })
    }
  }
}
</script>

<style></style>
