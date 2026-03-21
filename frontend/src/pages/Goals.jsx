import { useState, useEffect } from 'react'
import { Box, VStack, HStack, Text, Heading, Card, CardBody, CardHeader, SimpleGrid, Badge, Button, Input, InputGroup, InputLeftElement, Select, Progress, IconButton, Menu, MenuButton, MenuList, MenuItem } from '@chakra-ui/react'
import { FiPlus, FiSearch, FiFilter, FiMoreVertical, FiTarget, FiEdit2, FiTrash2, FiCheck, FiClock } from 'react-icons/fi'
import { dashboardAPI } from '../services/api'

function Goals() {
  const [goals, setGoals] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const [search, setSearch] = useState('')

  useEffect(() => {
    loadGoals()
  }, [])

  const loadGoals = async () => {
    try {
      const response = await dashboardAPI.getGoals()
      setGoals(response.data.goals || [])
    } catch (err) {
      console.error('Failed to load goals:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'green'
      case 'completed': return 'blue'
      case 'paused': return 'gray'
      default: return 'gray'
    }
  }

  const filteredGoals = goals.filter(g => {
    if (filter !== 'all' && g.status !== filter) return false
    if (search && !g.title.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between">
          <Heading size="lg">Goals</Heading>
          <Button leftIcon={<FiPlus />} colorScheme="brand">New Goal</Button>
        </HStack>

        {/* Filters */}
        <HStack>
          <InputGroup maxW="300px">
            <InputLeftElement><FiSearch /></InputLeftElement>
            <Input placeholder="Search goals..." value={search} onChange={(e) => setSearch(e.target.value)} />
          </InputGroup>
          <Select maxW="150px" value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="all">All</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
            <option value="paused">Paused</option>
          </Select>
        </HStack>

        {/* Goals Grid */}
        {loading ? (
          <Text>Loading...</Text>
        ) : filteredGoals.length === 0 ? (
          <Card><CardBody textAlign="center" py={12}><Text fontSize="3xl">🎯</Text><Text mt={4} color="gray.500">No goals yet. Create your first goal!</Text></CardBody></Card>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
            {filteredGoals.map(goal => (
              <Card key={goal.id}>
                <CardBody>
                  <HStack justify="space-between" mb={2}>
                    <Badge colorScheme={getStatusColor(goal.status)}>{goal.status}</Badge>
                    <Menu>
                      <MenuButton as={IconButton} icon={<FiMoreVertical />} variant="ghost" size="sm" />
                      <MenuList>
                        <MenuItem icon={<FiEdit2 />}>Edit</MenuItem>
                        <MenuItem icon={goal.status === 'active' ? <FiClock /> : <FiCheck />}>
                          {goal.status === 'active' ? 'Pause' : 'Resume'}
                        </MenuItem>
                        <MenuItem icon={<FiTrash2 />} color="red.500">Delete</MenuItem>
                      </MenuList>
                    </Menu>
                  </HStack>
                  <Heading size="sm" mb={2}>{goal.title}</Heading>
                  {goal.description && <Text fontSize="sm" color="gray.500" mb={3} noOfLines={2}>{goal.description}</Text>}
                  <Progress value={goal.progress} colorScheme="brand" size="sm" borderRadius="full" mb={2} />
                  <HStack justify="space-between">
                    <Text fontSize="xs" color="gray.500">{goal.progress}% complete</Text>
                    {goal.category && <Badge variant="subtle" fontSize="xs">{goal.category}</Badge>}
                  </HStack>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>
        )}
      </VStack>
    </Box>
  )
}

export default Goals
