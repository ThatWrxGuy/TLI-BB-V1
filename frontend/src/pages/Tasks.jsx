import { useState, useEffect } from 'react'
import { Box, VStack, HStack, Text, Heading, Card, CardBody, CardHeader, SimpleGrid, Badge, Button, Input, InputGroup, InputLeftElement, Select, Checkbox, IconButton, Menu, MenuButton, MenuList, MenuItem } from '@chakra-ui/react'
import { FiPlus, FiSearch, FiFilter, FiMoreVertical, FiEdit2, FiTrash2, FiClock } from 'react-icons/fi'
import { dashboardAPI } from '../services/api'

function Tasks() {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const [search, setSearch] = useState('')

  useEffect(() => {
    loadTasks()
  }, [])

  const loadTasks = async () => {
    try {
      const response = await dashboardAPI.getTasks()
      setTasks(response.data.tasks || [])
    } catch (err) {
      console.error('Failed to load tasks:', err)
    } finally {
      setLoading(false)
    }
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'red'
      case 'medium': return 'orange'
      case 'low': return 'green'
      default: return 'gray'
    }
  }

  const filteredTasks = tasks.filter(t => {
    if (filter === 'completed' && !t.is_completed) return false
    if (filter === 'pending' && t.is_completed) return false
    if (filter !== 'all' && filter !== 'completed' && filter !== 'pending' && t.priority !== filter) return false
    if (search && !t.title.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between">
          <Heading size="lg">Tasks</Heading>
          <Button leftIcon={<FiPlus />} colorScheme="brand">New Task</Button>
        </HStack>

        {/* Filters */}
        <HStack>
          <InputGroup maxW="300px">
            <InputLeftElement><FiSearch /></InputLeftElement>
            <Input placeholder="Search tasks..." value={search} onChange={(e) => setSearch(e.target.value)} />
          </InputGroup>
          <Select maxW="150px" value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="all">All</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
            <option value="high">High Priority</option>
            <option value="medium">Medium Priority</option>
            <option value="low">Low Priority</option>
          </Select>
        </HStack>

        {/* Tasks List */}
        {loading ? (
          <Text>Loading...</Text>
        ) : filteredTasks.length === 0 ? (
          <Card><CardBody textAlign="center" py={12}><Text fontSize="3xl">✅</Text><Text mt={4} color="gray.500">No tasks yet. Create your first task!</Text></CardBody></Card>
        ) : (
          <VStack spacing={3} align="stretch">
            {filteredTasks.map(task => (
              <Card key={task.id}>
                <CardBody>
                  <HStack spacing={4}>
                    <Checkbox isChecked={task.is_completed} colorScheme="brand" size="lg" />
                    <VStack align="start" spacing={0} flex={1}>
                      <Text fontWeight="500" textDecoration={task.is_completed ? 'line-through' : 'none'} color={task.is_completed ? 'gray.400' : 'inherit'}>
                        {task.title}
                      </Text>
                      {task.due_date && <Text fontSize="xs" color="gray.500">Due: {task.due_date}</Text>}
                    </VStack>
                    <Badge colorScheme={getPriorityColor(task.priority)} variant="subtle">{task.priority}</Badge>
                    <Menu>
                      <MenuButton as={IconButton} icon={<FiMoreVertical />} variant="ghost" size="sm" />
                      <MenuList>
                        <MenuItem icon={<FiEdit2 />}>Edit</MenuItem>
                        <MenuItem icon={task.is_completed ? <FiClock /> : <FiEdit2 />}>
                          {task.is_completed ? 'Mark Incomplete' : 'Mark Complete'}
                        </MenuItem>
                        <MenuItem icon={<FiTrash2 />} color="red.500">Delete</MenuItem>
                      </MenuList>
                    </Menu>
                  </HStack>
                </CardBody>
              </Card>
            ))}
          </VStack>
        )}

        {/* Stats */}
        <SimpleGrid columns={4} spacing={4}>
          <Card><CardBody textAlign="center"><Text fontSize="2xl" fontWeight="bold">{tasks.length}</Text><Text fontSize="sm" color="gray.500">Total</Text></CardBody></Card>
          <Card><CardBody textAlign="center"><Text fontSize="2xl" fontWeight="bold" color="green.500">{tasks.filter(t => t.is_completed).length}</Text><Text fontSize="sm" color="gray.500">Completed</Text></CardBody></Card>
          <Card><CardBody textAlign="center"><Text fontSize="2xl" fontWeight="bold" color="orange.500">{tasks.filter(t => t.priority === 'high' && !t.is_completed).length}</Text><Text fontSize="sm" color="gray.500">High Priority</Text></CardBody></Card>
          <Card><CardBody textAlign="center"><Text fontSize="2xl" fontWeight="bold">{tasks.filter(t => !t.is_completed).length}</Text><Text fontSize="sm" color="gray.500">Pending</Text></CardBody></Card>
        </SimpleGrid>
      </VStack>
    </Box>
  )
}

export default Tasks
