import { createRouter, createWebHistory } from 'vue-router'
import { authenticated, refreshSession, sessionReady } from '../auth/session'
import { postLoginTarget } from '../utils/postLoginRedirect'
import LoginView from '../views/LoginView.vue'
import PersonList from '../views/PersonList.vue'
import PersonDetail from '../views/PersonDetail.vue'
import SessionDetail from '../views/SessionDetail.vue'
import ObservationsView from '../views/ObservationsView.vue'
import TrendsView from '../views/TrendsView.vue'
import IndicatorsView from '../views/IndicatorsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
    { path: '/', component: PersonList },
    {
      path: '/persons/:personId/current-abnormals',
      component: ObservationsView,
      props: (route) => ({
        personId: String(route.params.personId),
        reportMode: 'current-abnormal' as const,
      }),
    },
    { path: '/persons/:personId', component: PersonDetail, props: true },
    {
      path: '/persons/:personId/sessions/:sessionId',
      component: SessionDetail,
      props: true,
    },
    {
      path: '/persons/:personId/observations',
      component: ObservationsView,
      props: true,
    },
    {
      path: '/persons/:personId/trends',
      component: TrendsView,
      props: true,
    },
    { path: '/indicators', component: IndicatorsView },
  ],
})

router.beforeEach(async (to) => {
  if (!sessionReady.value) {
    await refreshSession()
  }

  const authed = authenticated.value

  if (to.name === 'login') {
    if (authed) {
      const r = postLoginTarget(to.query.redirect)
      return r
    }
    return true
  }

  if (!authed) {
    return {
      path: '/login',
      query: {
        redirect: to.fullPath === '/' ? '/' : to.fullPath,
      },
    }
  }

  return true
})

export default router
