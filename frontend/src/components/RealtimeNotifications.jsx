import { useState, useEffect } from 'react'
import { Box, VStack, HStack, Text, IconButton, Badge, useToast } from '@chakra-ui/react'
import { FiBell, FiX, FiCheck, FiAlertCircle, FiInfo } from 'react-icons/fi'
import { useRealtimeNotifications } from '../hooks/useWebSocket'

const MAX_NOTIFICATIONS = 10

function NotificationToast({ notification, onClose }) {
  const getIcon = () => {
    switch (notification.type) {
      case 'success':
        return <FiCheck color="green" />
      case 'error':
        return <FiAlertCircle color="red" />
      default:
        return <FiInfo color="blue" />
    }
  }

  return (
    <HStack
      p={4}
      bg="white"
      borderRadius="lg"
      boxShadow="lg"
      spacing={3}
      minW="300px"
      borderLeft="4px solid"
      borderLeftColor={
        notification.type === 'success' ? 'green.500' :
        notification.type === 'error' ? 'red.500' :
        'blue.500'
      }
    >
      <Box fontSize="xl">{getIcon()}</Box>
      <VStack align="start" spacing={0} flex={1}>
        <Text fontWeight="600" fontSize="sm">{notification.title}</Text>
        <Text fontSize="xs" color="gray.600">{notification.message}</Text>
      </VStack>
      <IconButton
        size="xs"
        variant="ghost"
        icon={<FiX />}
        onClick={onClose}
      />
    </HStack>
  )
}

function RealtimeNotifications() {
  const { notifications, unreadCount, clearAll } = useRealtimeNotifications()
  const [showPanel, setShowPanel] = useState(false)
  const [toastNotifications, setToastNotifications] = useState([])
  const toast = useToast()

  // Show toast for new notifications
  useEffect(() => {
    if (notifications.length > 0) {
      const latest = notifications[0]
      
      // Show toast if it's a new notification
      if (!toastNotifications.find(n => n.id === latest.id)) {
        toast({
          position: 'top-right',
          render: ({ onClose }) => (
            <NotificationToast 
              notification={latest} 
              onClose={onClose} 
            />
          ),
          duration: 5000,
          isClosable: true,
        })
        
        setToastNotifications(prev => [...prev, latest])
        
        // Keep only last 10
        if (toastNotifications.length >= MAX_NOTIFICATIONS) {
          setToastNotifications(prev => prev.slice(-MAX_NOTIFICATIONS + 1))
        }
      }
    }
  }, [notifications])

  return (
    <>
      {/* Notification Bell */}
      <Box position="relative" display="inline-block">
        <IconButton
          icon={<FiBell />}
          variant="ghost"
          aria-label="Notifications"
          onClick={() => setShowPanel(!showPanel)}
        />
        {unreadCount > 0 && (
          <Badge
            position="absolute"
            top={0}
            right={0}
            colorScheme="red"
            borderRadius="full"
            fontSize="xs"
            minW={5}
            h={5}
            display="flex"
            alignItems="center"
            justifyContent="center"
          >
            {unreadCount > 9 ? '9+' : unreadCount}
          </Badge>
        )}
      </Box>

      {/* Notification Panel */}
      {showPanel && (
        <Box
          position="absolute"
          top={14}
          right={0}
          w="350px"
          maxH="400px"
          bg="white"
          borderRadius="xl"
          boxShadow="xl"
          overflow="hidden"
          zIndex={1000}
        >
          <HStack justify="space-between" p={4} borderBottom="1px" borderColor="gray.100">
            <Text fontWeight="600">Notifications</Text>
            {notifications.length > 0 && (
              <Text
                fontSize="xs"
                color="brand.500"
                cursor="pointer"
                onClick={clearAll}
              >
                Clear all
              </Text>
            )}
          </HStack>

          <Box maxH="350px" overflowY="auto">
            {notifications.length === 0 ? (
              <Box p={8} textAlign="center">
                <Text fontSize="3xl">🔔</Text>
                <Text color="gray.500" mt={2}>No notifications</Text>
              </Box>
            ) : (
              <VStack spacing={0} align="stretch">
                {notifications.slice(0, 10).map((notif, index) => (
                  <HStack
                    key={notif.id || index}
                    p={3}
                    spacing={3}
                    _hover={{ bg: 'gray.50' }}
                    borderBottom="1px"
                    borderColor="gray.50"
                    cursor="pointer"
                  >
                    <Box
                      w={2}
                      h={2}
                      borderRadius="full"
                      bg={notif.read ? 'gray.300' : 'brand.500'}
                    />
                    <VStack align="start" spacing={0} flex={1}>
                      <Text fontSize="sm" fontWeight="500" noOfLines={1}>
                        {notif.title}
                      </Text>
                      <Text fontSize="xs" color="gray.500" noOfLines={2}>
                        {notif.message}
                      </Text>
                    </VStack>
                  </HStack>
                ))}
              </VStack>
            )}
          </Box>
        </Box>
      )}
    </>
  )
}

export default RealtimeNotifications
