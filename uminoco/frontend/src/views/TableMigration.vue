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
              Source and Destination tables
            </v-stepper-step>
            <v-stepper-content step="1">
              <v-container>

                <div v-if="tableNames">
                  <v-row>
                    <v-col key="1" cols="12" sm="6">
                      <v-select v-model="srcTableName" :items="tableNames" label="Source" required></v-select>
                    </v-col>
                    <v-col key="2" cols="12"  sm="6">
                      <v-select v-model="dstTableName" :items="tableNames" label="Destination" required></v-select>
                    </v-col>
                  </v-row>
                </div>

              <v-btn color="primary" @click="stepperModel = 2" :disabled="!!(!srcTableName || !dstTableName)">Continue
                <v-icon v-if="!!(!srcTableName || !dstTableName)" dark right>mdi-cancel</v-icon>
                <v-icon v-else dark right>mdi-checkbox-marked-circle</v-icon>
              </v-btn>

              </v-container>

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
                  <!-- <v-card> -->

                    <!-- Tdbles -->
                    <v-row no-gutters>
                      <v-col class="" key="1" cols="5" sm="5">
                        <p class="text-right">{{this.srcTableName}}</p>
                      </v-col>
                      <v-col class="text-center mb-4" key="2" cols="2" sm="2"><p class="headline mb-1">➡</p></v-col>
                      <v-col class="text-left" key="3" cols="5" sm="5">
                        <p class="">{{this.dstTableName}}</p>
                      </v-col>
                    </v-row>

                    <v-simple-table>
                      <template v-slot:default>
                        <!-- Header -->
                        <thead>
                          <tr>
                            <th class="text-left">Source Types</th>
                            <th class="text-left">Source Columns</th>
                            <th class="text-left"></th>
                            <th class="text-left">Dest Columns</th>
                            <th class="text-left">Dest Types</th>
                          </tr>
                        </thead>

                        <!-- Each columns -->
                        <tbody>
                          <tr v-for="(item, index) in dstColumns" :key="item.position">

                            <!-- Source type -->
                            <td>
                              <div v-if="selectedSrcColumnNames[index] && getSourceColumn(index)">
                                <v-chip class="ms-2" color="blue-grey" text-color="white">
                                  <v-avatar left><v-icon>{{getTypeIcon(getSourceColumn(index).type)}}</v-icon></v-avatar>
                                  {{getSourceColumn(index).type}}
                                </v-chip>
                              </div>
                              <div v-else>
                                <v-tooltip top>
                                  <template v-slot:activator="{ on, attrs }">
                                    <v-chip class="ms-2" color="blue-grey lighten-3" text-color="white" v-bind="attrs" v-on="on">
                                      <v-avatar left><v-icon>{{getTypeIcon(null)}}</v-icon></v-avatar> NULL
                                    </v-chip>
                                  </template>
                                  <span>NULL will be used instead of source table values.</span>
                                </v-tooltip>
                              </div>
                            </td>

                            <!-- Source Column -->
                            <td>
                              <v-select :items="Object.keys(srcColumnsMap)" dense
                                v-model="selectedSrcColumnNames[index]"
                                :clearable=true >
                              </v-select>
                            </td>

                            <!-- Sep -->
                            <td>
                              <v-chip v-if="getTypeCompatibilityStatus(getSourceColumn(index), item.type) === 'ok'" class="ms-2" color="green" text-color="white">
                                <v-avatar center><v-icon>mdi-check</v-icon></v-avatar>
                              </v-chip>
                              <div v-else>
                                <v-tooltip top>
                                  <template v-slot:activator="{ on, attrs }">
                                    <v-chip  class="ms-2" color="warning" text-color="white" v-bind="attrs" v-on="on">
                                      <v-avatar center><v-icon>mdi-alert</v-icon></v-avatar>
                                    </v-chip>
                                  </template>
                                  <span>Data type is not euqual. Data will be inserted depends on implementation of database.</span>
                                </v-tooltip>
                              </div>
                            </td>

                            <!-- Dst Column -->
                            <td>{{item.name}}</td>

                            <!-- Dst Type -->
                            <td>
                              <v-chip class="ms2" color="blue-grey" text-color="white">
                                <v-avatar left><v-icon>
                                  {{getTypeIcon(item.type)}}
                                </v-icon></v-avatar>
                                {{item.type}}
                              </v-chip>
                            </td>

                          </tr>
                        </tbody>
                      </template>
                    </v-simple-table>

                  <!-- </v-card> -->

                </div><!-- v-if="this.dstColumns" -->
              </v-container>

              <v-btn color="primary" @click=migrate :loading="isMigrating">Migrate!</v-btn>
              <v-btn text @click="stepperModel = 1" :disabled="isMigrating" >Back</v-btn>
            </v-stepper-content>

          </v-stepper>
        </v-col>
      </v-row>

      <!-- Migrating Dialog -->
      <v-dialog v-model="isMigrating" max-width="320" persistent>
        <v-card color="primary" dark >
          <v-card-text>
            Migrating...
            <v-progress-linear indeterminate color="white" class="mb-0"></v-progress-linear>
          </v-card-text>
        </v-card>
      </v-dialog>

      <!-- Migration Result Dialog -->
      <v-dialog v-model="isCompleted" max-width="320">
        <div v-if="migrationFailer">
          <v-card color="warning">
            <v-card-title class="headline">
              <v-icon large left>mdi-alert</v-icon> Migration Failed... </v-card-title>
            <v-card-text> {{this.migrationFailer}} </v-card-text>
            <v-card-actions>
              <v-btn text @click="isCompleted = false"> Close </v-btn>
            </v-card-actions>
          </v-card>
        </div>
        <div v-else>
          <v-card>
            <v-card-title class="headline">
              <v-icon large left>mdi-check</v-icon>Migration Succeeded!</v-card-title>
            <v-card-actions>
              <v-btn text @click="isCompleted = false"> OK! </v-btn>
            </v-card-actions>
          </v-card>
        </div>
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
            this.reCreateColumnMap()
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
            this.reCreateColumnMap()
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
    reCreateColumnMap() {
      if (this.srcTableData && this.dstTableData) {
        this.srcColumnsMap = {}
        for (const idx in this.srcTableData.columns) {
          var src = this.srcTableData.columns[idx]
          this.srcColumnsMap[src.name] = src
        }
        this.dstColumns = this.dstTableData.columns.slice().sort((a, b) => a - b)
        this.selectedSrcColumnNames = []
        for (var idx in this.dstColumns) {
          var dst = this.dstColumns[idx]
          this.selectedSrcColumnNames[idx] = this.srcTableData.columns.find(src => dst.name === src.name)?.name
        }
      }
    },
    getSourceColumn (index) {
      return this.srcColumnsMap[this.selectedSrcColumnNames[index]]
    },
    getTypeCompatibilityStatus (fromType, toType) {
      const tl = toType.toLowerCase()
      if (tl.includes('str') || tl.includes('char')) return 'ok'
      if (!fromType) return 'ok'

      if (fromType.type === toType) return 'ok'

      return 'warn'
    },
    getTypeIcon (type) {
      if (type === null) return 'mdi-null'

      const tl = type.toLowerCase()
      if (tl.includes('arr')) {
        return 'mdi-code-brackets'
      }
      if (tl.includes('str') || tl.includes('char')) {
        return 'mdi-syllabary-hiragana'
      }
      if (tl.includes('int') || tl.includes('num') || tl.includes('float') || tl.includes('double')) {
        return 'mdi-numeric'
      }
      if (tl.includes('cal') || tl.includes('date') || tl.includes('time')) {
        return 'mdi-calendar-range'
      }
      if (tl.includes('uuid')) {
        return 'mdi-card-account-details-outline'
      }
      return 'mdi-table-column'
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
