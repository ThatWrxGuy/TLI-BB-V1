import { useState, useEffect } from 'react'
import { Box, VStack, HStack, Text, Heading, Card, CardBody, Badge, Button, IconButton, Select, Tabs, TabList, Tab, TabPanels, TabPanel } from '@chakra-ui/react'
import { FiBell, FiCheck, FiTrash2, FiSettings, FiAlertCircle, FiInfo, FiCheckCircle } from 'react-icons/fi'
import { useAuth } from '../context/AuthContext'

function NotificationItem({ notification, onMarkRead, onDelete }) {
  const getIcon = (type) => {
    switch (type) {
      case 'success': return <FiCheckCircle color="green" />
      case 'warning': return <FiAlertCircle color="orange" />
      case 'error': return <FiAlertCircle color="red" />
      default: return <FiInfo color="blue" />
    }
  }

  return (
    <HStack p={4} borderBottom="1px" borderColor="gray.100" spacing={4}>
      <Box p={2} borderRadius="lg" bg="gray.50">
        {getIcon(notification.type)}
      </Box>
      <VStack align="start" spacing={0} flex={1}>
        <Text fontWeight="500">{notification.title}</Text>
        <Text fontSize="sm" color="gray.500">{notification.message}</Text>
        <Text fontSize="xs" color="gray.400">{notification.time}</Text>
      </VStack>
      <VStack>
        {!notification.read && <Button size="xs" onClick={() => onMarkRead(notification.id)}>Mark Read</Button>}
        <IconButton icon={<FiTrash2 />} size="xs" variant="ghost" colorScheme="red" onClick={() => onDelete(notification.id)} />
      </VStack>
    </HStack>
  )
}

function Notifications() {
  const { user } = useAuth()
  const [notifications, setNotifications] = useState([])
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    // Demo notifications
    setNotifications([
      { id: 1, type: 'success', title: 'Goal Completed!', message: 'You completed "Learn Python" goal!', time: '2 hours ago', read: false },
      { id: 2, type: 'info', title: 'New Feature Available', message: 'Check out the new Analytics dashboard', time: '1 day ago', read: true },
      { id: 3, type: 'warning', title: 'Streak at Risk', message: 'Complete a task today to keep your streak!', time: '2 days ago', read: false },
      { id: 4, type: 'info', title: 'Welcome to Busy Bee!', message: 'Start by creating your first goal', time: '1 week ago', read: true },
    ])
  }, [])

  const markAsRead = (id) => {
    setNotifications(notifications.map(n => n.id === id ? { ...n, read: true } : n))
  }

  const markAllRead = () => {
    setNotifications(notifications.map(n => ({ ...n, read: true })))
  }

  const deleteNotification = (id) => {
    setNotifications(notifications.filter(n => n.id !== id))
  }

  const clearAll = () => {
    setNotifications([])
  }

  const filtered = notifications.filter(n => {
    if (filter === 'unread') return !n.read
    if (filter === 'read') return n.read
    return true
  })

  const unreadCount = notifications.filter(n => !n.read).length

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between">
          <HStack>
            <Heading size="lg">Notifications</Heading>
            {unreadCount > 0 && <Badge colorScheme="red">{unreadCount} new</Badge>}
          </HStack>
          <HStack>
            <Button size="sm" variant="ghost" onClick={markAllRead}>Mark all read</Button>
            <Button size="sm" variant="ghost" colorScheme="red" onClick={clearAll}>Clear all</Button>
          </HStack>
        </HStack>

        {/* Filters */}
        <Tabs onChange={(index) => setFilter(['all', 'unread', 'read'][index])}>
          <TabList>
            <Tab>All ({notifications.length})</Tab>
            <Tab>Unread ({unreadCount})</Tab>
            <Tab>Read ({notifications.filter(n => n.read).length})</Tab>
          </TabList>
        </Tabs>

        {/* Notifications List */}
        {filtered.length === 0 ? (
          <Card><CardBody textAlign="center" py={12}><Text fontSize="3xl">🔔</Text><Text mt={4} color="gray.500">No notifications</Text></CardBody></Card>
        ) : (
          <Card>
            <CardBody p={0}>
              {filtered.map(n => (
                <NotificationItem key={n.id} notification={n} onMarkRead={markAsRead} onDelete={deleteNotification} />
              ))}
            </CardBody>
          </Card>
        )}
      </VStack>
    </Box>
  )
}

export default Notifications
