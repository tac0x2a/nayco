<template>
  <div>
    <v-container>
      <v-banner>
        <p class="display-1 text--primary">Now in shipbuilding...</p>
        <template v-slot:actions>
          <v-btn
            text
            color="indigo"
            href="https://github.com/tac0x2a/nayco"
            target="_blank"
          >View on Github</v-btn>
        </template>
      </v-banner>

      <v-row>
        <v-col key="1" cols="12" sm="4">
          <v-card class="mx-auto">
            <v-card-text>
              <p class="display-1 text--primary">Manage Tables</p>
              <div class="text--primary">
                You can rename and delete tables, see what storage and compression rates are being used.
              </div>
            </v-card-text>
            <v-card-actions>
              <v-btn text color="indigo accent-4" to="/table">Open Tables</v-btn>
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
