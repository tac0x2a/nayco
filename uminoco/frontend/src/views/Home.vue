<template>
  <div>
    <v-container>
      <v-banner>
        <p class="display-1 text--primary">Now in shipbuilding...🚢🔧</p>
        <template v-slot:actions>
          <v-btn
            text
            color="primary"
            href="https://github.com/tac0x2a/nayco"
            target="_blank"
          >View on Github</v-btn>
        </template>
      </v-banner>

      <v-row align="stretch">
        <v-col key="1" cols="12" sm="4">
          <v-card class="mx-auto" height="100%">
            <v-card-text>
              <v-icon>mdi-table-large</v-icon>
              <p class="display-1 text--primary">Tables Manager</p>
              <div class="text--primary">
                You can rename and delete tables, see what storage and compression rates are being used.
              </div>
            </v-card-text>
            <v-card-actions>
              <v-btn text color="primary accent-4" to="/table">Open</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>

        <v-col key="1" cols="12" sm="4">
          <v-card class="mx-auto" height="100%">
            <v-card-text>
              <v-icon>mdi-call-merge</v-icon>
              <p class="display-1 text--primary">Migration Tables</p>
              <div class="text--primary">
                You can copy table data into other table.
                This feature is expected to use when created new table by receiving schema similer to old one. You can integrate data into new table.
              </div>
            </v-card-text>
            <v-card-actions>
              <v-btn text color="primary accent-4" to="/table_migration">Open</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>

        <v-col key="1" cols="12" sm="4">
          <v-card class="mx-auto" height="100%">
            <v-card-text>
              <v-icon>mdi-water</v-icon>
              <p class="display-1 text--primary">Data Source Manager</p>
              <div class="text--primary">
                View the List fo data sources.
                You can edit the specified types to correct data type on Grebe.
              </div>
            </v-card-text>
            <v-card-actions>
              <v-btn text color="primary accent-4" to="/source">Open</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>

      </v-row>
    </v-container>
  </div>
</template>

<script>
export default {
  name: 'Home',
  components: {}
}
</script>
