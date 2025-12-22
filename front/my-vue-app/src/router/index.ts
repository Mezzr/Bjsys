import { createRouter, createWebHistory } from 'vue-router'

const PartsList = () => import('../pages/PartsList.vue')
const PartDetail = () => import('../pages/PartDetail.vue')
const PartForm = () => import('../pages/PartForm.vue')

const routes = [
  { path: '/', redirect: '/parts' },
  { path: '/parts', name: 'PartsList', component: PartsList },
  { path: '/parts/new', name: 'PartCreate', component: PartForm },
  { path: '/parts/:id', name: 'PartDetail', component: PartDetail, props: true },
  { path: '/parts/:id/edit', name: 'PartEdit', component: PartForm, props: true }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
