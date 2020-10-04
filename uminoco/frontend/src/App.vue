<template>
  <v-app id="App">
    <v-navigation-drawer v-model="drawer" app>
      <v-list dense>

        <v-list-item to="/">
          <v-list-item-action>
            <v-icon>mdi-ferry</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Home</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-divider></v-divider>

        <v-list-item to="/source">
          <v-list-item-action>
            <!-- <v-icon>mdi-duck</v-icon> -->
            <v-icon>mdi-water</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Data Sources</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-divider></v-divider>

        <v-list-item to="/table">
          <v-list-item-action>
            <v-icon>mdi-table-large</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Tables</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item to="/table_migration">
          <v-list-item-action>
            <v-icon>mdi-call-merge</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>TableMigration</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-divider></v-divider>

      </v-list>
    </v-navigation-drawer>

    <v-app-bar app color="indigo" dark>
      <v-app-bar-nav-icon @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title>Uminoco</v-toolbar-title>
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>

    <v-footer color="indigo" app>
      <span class="white--text"> tac0x2a &copy; {{ new Date().getFullYear() }} </span>
    </v-footer>

  </v-app>
</template>

<script>

export default {
  name: 'App',

  components: {},

  props: {
    source: String
  },

  data: () => ({
    drawer: null
  })
}
</script>
