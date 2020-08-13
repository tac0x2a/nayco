<template>
  <div>
    <v-container>
      <v-banner>
        <p class="display-1 text--primary">Now in shipbuilding...</p>
        <template v-slot:actions>
          <v-btn text color="indigo" href="https://github.com/tac0x2a/nayco" target="_blank">View on Github</v-btn>
        </template>
      </v-banner>
    </v-container>
  </div>
</template>

<script>
export default {
  name: 'Home',
  components: {}
}
</script>
