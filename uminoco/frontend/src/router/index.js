import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '@/views/Home.vue'
import Table from '@/views/Table.vue'
import Develop from '@/views/Develop.vue'

Vue.use(VueRouter)

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/table', name: 'Table', component: Table },
  { path: '/develop', name: 'Develop', component: Develop }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
