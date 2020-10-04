import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '@/views/Home.vue'
import Tables from '@/views/Tables.vue'
import Table from '@/views/Table.vue'
import TableMigration from '@/views/TableMigration.vue'
import Sources from '@/views/Sources.vue'
import SourceTypeSettings from '@/views/SourceTypeSettings.vue'

Vue.use(VueRouter)

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/table', name: 'Tables', component: Tables },
  { path: '/table/:tableName', name: 'Table', component: Table, props: (route) => ({ tableName: route.params.tableName }) },
  { path: '/table_migration', name: 'TableMigration', component: TableMigration },
  { path: '/source', name: 'Sources', component: Sources },
  { path: '/source_types/:sourceId', name: 'SourceTypeSettings', component: SourceTypeSettings, props: (route) => ({ sourceId: route.params.sourceId }) }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
