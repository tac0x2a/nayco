<template>
  <div>
    <v-breadcrumbs :items="breadcrumbs">
      <template v-slot:divider>
        <v-icon>mdi-chevron-right</v-icon>
      </template>
    </v-breadcrumbs>

    <v-container>
      <v-row no-gutters>
        <v-col key="1" cols="12" sm="12">
          <v-stepper v-model="stepperModel" vertical>

            <!-- Step 1. Select Tables -->
            <v-stepper-step :complete="stepperModel > 1" step="1" :editable=true>
              <p class="headline mb-1">Select Tables</p>
              From and Destination table
            </v-stepper-step>
            <v-stepper-content step="1">
              <v-container>
                <div v-if="tableNames">
                  <v-row no-gutters>
                    <v-col class="pr-8" key="1" cols="12" sm="6">
                      <v-select v-model="srcTableName" :items="tableNames" label="From" required></v-select>
                    </v-col>
                    <v-col class="pl-8" key="2" cols="12" sm="6">
                      <v-select v-model="dstTableName" :items="tableNames" label="To" required></v-select>
                    </v-col>
                  </v-row>
                </div>
              </v-container>
              <v-btn color="primary" @click="stepperModel = 2" :disabled="!!(!srcTableName || !dstTableName)">Continue</v-btn>
            </v-stepper-content>

            <!-- Step 2. Select Columns -->
            <v-stepper-step :complete="stepperModel > 2" step="2" :editable="!!(srcTableName && dstTableName)">
              <p class="headline mb-1">Select Columns</p>
              Set source and destination columns
            </v-stepper-step>
            <v-stepper-content step="2">
              <v-container>

                <!-- Each columns -->
                <div v-if="this.dstColumns">

                  <!-- Tdbles -->
                  <v-row no-gutters>
                    <v-col class="pa-0" key="1" cols="12" sm="1"><p class="headline mb-1"></p></v-col>
                    <v-col class="pa-0" key="4" cols="12" sm="4">
                      <v-card><p class="headline mb-1">{{this.srcTableName}}</p></v-card>
                    </v-col>

                    <v-col class="pa-0" key="2" cols="12" sm="1"><p class="headline mb-1">👉</p></v-col>

                    <v-col class="pa-0" key="3" cols="12" sm="6">
                      <v-card><p class="headline mb-1">{{this.dstTableName}}</p></v-card>
                    </v-col>
                  </v-row>

                  <!-- Header -->
                  <v-card>
                    <v-row no-gutters>
                      <v-col class="pa-1" key="1" cols="12" sm="1">No.</v-col>
                      <v-col class="pa-1" key="6" cols="12" sm="3">Types</v-col>
                      <v-col class="pa-1" key="2" cols="12" sm="2">Columns</v-col>

                      <v-col class="pa-1" key="3" cols="12" sm="1"></v-col>

                      <v-col class="pa-1" key="4" cols="12" sm="2">Columns</v-col>
                      <v-col class="pa-1" key="5" cols="12" sm="4">Types</v-col>
                    </v-row>
                  </v-card>

                  <!-- Each columns -->
                  <v-card>
                    <div v-for="(item, index) in this.dstColumns" :key="item.position">
                      <v-row no-gutters>
                        <v-col class="pa-1" key="1" cols="12" sm="1">{{item.position}}</v-col>

                        <v-col class="pa-1" key="2" cols="12" sm="2">
                          <v-chip v-if="selectedSrcColumnNames[index] && srcColumnsMap[selectedSrcColumnNames[index]]" class="ma-1" color="indigo" text-color="white">
                            <v-avatar left><v-icon>{{getTypeIcon(srcColumnsMap[selectedSrcColumnNames[index]].type)}}</v-icon></v-avatar>
                            {{srcColumnsMap[selectedSrcColumnNames[index]].type}}
                          </v-chip>
                          <v-chip v-else class="ma-1" color="gray" text-color="white">
                            None
                          </v-chip>
                        </v-col>

                        <v-col class="pa-0" key="3" cols="12" sm="2">
                          <v-select :items="Object.keys(srcColumnsMap)" dense
                          v-model="selectedSrcColumnNames[index]">
                          </v-select>
                        </v-col>

                        <v-col class="pa-1" key="4" cols="12" sm="1">👉</v-col>

                        <v-col class="pa-1" key="5" cols="12" sm="2">{{item.name}}</v-col>
                        <v-col class="p1-1" key="6" cols="12" sm="4">
                          <v-chip class="ma-1" color="indigo" text-color="white">
                            <v-avatar left><v-icon>
                              {{getTypeIcon(item.type)}}
                            </v-icon></v-avatar>
                            {{item.type}}
                          </v-chip>
                        </v-col>
                      </v-row>
                    </div> <!-- v-for="item in this.dstColumns" :key="item.position" -->
                  </v-card>

                </div><!-- v-if="this.dstColumns" -->
              </v-container>

              <v-btn color="primary" @click=migrate :loading="isMigrating">Migrate!</v-btn>
              <v-btn text @click="stepperModel = 1" :disabled="isMigrating" >Back</v-btn>
            </v-stepper-content>

          </v-stepper>
        </v-col>
      </v-row>

      <v-dialog v-model="isCompleted" max-width="290">
        <v-card>
          <div v-if="migrationFailer">
            <v-card-title class="headline">Migration Failed...</v-card-title>
          </div>
          <div v-else>
            <v-card-title class="headline">Migration Success!</v-card-title>
            <v-card-text>
              {{this.migrationFailer}}
            </v-card-text>
          </div>

        <v-card-actions>
          <v-btn color="green darken-1" text @click="isCompleted = false">
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    </v-container>
  </div>
</template>

<script>
import Clickhouse from '@/api/clickhouse.js'

export default {
  props: ['pSrcTableName', 'pDstTableName'],

  components: {},

  data: () => ({
    breadcrumbs: [
      { text: 'Home', exact: true, disabled: false, to: { name: 'Home' } },
      { text: 'TableMigration', exact: true, disabled: false, to: { name: 'TableMigration' } }
    ],
    stepperModel: 1,
    tables: null,
    srcTableName: null,
    dstTableName: null,
    srcTableData: null,
    dstTableData: null,

    srcColumnsMap: {},
    dstColumns: null,
    selectedSrcColumnNames: [],

    isMigrating: false,
    isCompleted: false,
    migrationFailer: null
  }),

  computed: {
    tableNames() {
      return this.tables?.map(t => t.name)
    }
  },

  watch: {
    srcTableName: {
      handler() {
        if (this.srcTableName) {
          Clickhouse.tableDetail(this.srcTableName, res => {
            this.srcTableData = res

            this.srcColumnsMap = {}
            for (const idx in this.srcTableData.columns) {
              var src = this.srcTableData.columns[idx]
              this.srcColumnsMap[src.name] = src
            }
            if (this.srcTableData && this.dstTableData) {
              this.dstColumns = this.dstTableData.columns.slice().sort((a, b) => a - b)
              for (const idx in this.dstColumns) {
                var dst = this.dstColumns[idx]
                this.selectedSrcColumnNames[idx] = this.srcTableData.columns.find(src => dst.name === src.name)?.name
              }
            }
          },
          err => {
            this.failer = { error: err, message: err?.response?.data?.message }
          })
        }
      },
      immediate: true
    },
    dstTableName: {
      handler() {
        if (this.dstTableName) {
          Clickhouse.tableDetail(this.dstTableName, res => {
            this.dstTableData = res
            this.dstColumns = this.dstTableData.columns.slice().sort((a, b) => a - b)

            if (this.srcTableData && this.dstTableData) {
              for (var idx in this.dstColumns) {
                var dst = this.dstColumns[idx]
                this.selectedSrcColumnNames[idx] = this.srcTableData.columns.find(src => dst.name === src.name)?.name
              }
            }
          },
          err => {
            this.failer = { error: err, message: err?.response?.data?.message }
          })
        }
      },
      immediate: true
    }
  },

  mounted() {
    Clickhouse.listTables(res => {
      this.tables = res
      this.srcTableName = this.pSrcTableName
      this.dstTableName = this.pDstTableName
    })
  },

  methods: {
    getTypeIcon (type) {
      // Todo change icon by types
      return 'mdi-account-circle'
    },
    migrate() {
      const srcColNames = this.selectedSrcColumnNames.slice()
      const dstColNames = this.dstColumns.map(c => c.name)
      Clickhouse.migrateTable(this.srcTableName, this.dstTableName, srcColNames, dstColNames, res => {
        this.migrationFailer = null
        this.isMigrating = false
        this.isCompleted = true
      },
      err => {
        this.migrationFailer = err
        this.isMigrating = false
        this.isCompleted = true
      })

      this.isMigrating = true

      // Todo modal
    }
  }
}
</script>
