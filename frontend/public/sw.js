// Busy Bee — Service Worker
// public/sw.js
// Handles incoming push events and notification clicks

self.addEventListener('push', event => {
  if (!event.data) return

  let payload
  try { payload = event.data.json() }
  catch { payload = { title: 'Busy Bee', body: event.data.text() } }

  const { title, body, icon, badge, tag, url, actions } = payload

  event.waitUntil(
    self.registration.showNotification(title || 'Busy Bee 🐝', {
      body:    body    || '',
      icon:    icon    || '/icon-192.png',
      badge:   badge   || '/badge-72.png',
      tag:     tag     || 'busy-bee',
      data:    { url:  url || '/' },
      actions: actions || [],
      vibrate: [100, 50, 100],
      renotify: true,
    })
  )
})

self.addEventListener('notificationclick', event => {
  event.notification.close()

  const url = event.notification.data?.url || '/'

  // Handle action buttons
  if (event.action === 'checkin') {
    event.waitUntil(clients.openWindow('/domains'))
    return
  }
  if (event.action === 'goals') {
    event.waitUntil(clients.openWindow('/goals'))
    return
  }

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(list => {
      const existing = list.find(c => c.url.includes(self.location.origin))
      if (existing) { existing.focus(); existing.navigate(url) }
      else clients.openWindow(url)
    })
  )
})

// Keep service worker alive — skip waiting on install
self.addEventListener('install',  () => self.skipWaiting())
self.addEventListener('activate', e => e.waitUntil(clients.claim()))
