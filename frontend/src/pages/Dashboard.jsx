import { useState, useEffect } from 'react'
import { Box, Grid, GridItem, VStack, HStack, Text, Button, Card, CardBody, CardHeader, Heading, Stat, StatLabel, StatNumber, StatHelpText, Progress, Badge, IconButton, SimpleGrid, Spinner, Center } from '@chakra-ui/react'
import { FiPlus, FiCheck, FiClock, FiTrendingUp, FiTrendingDown, FiMinus, FiArrowRight } from 'react-icons/fi'
import { Link } from 'react-router-dom'
import { dashboardAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'

function StatCard({ icon: Icon, label, value, helpText, trend }) {
  return (
    <Card>
      <CardBody>
        <HStack justify="space-between" mb={2}>
          <Box p={2} bg="brand.50" rounded="lg">
            <Icon size={20} color="#F59E0B" />
          </Box>
          {trend && (
            <HStack spacing={1} fontSize="sm" color={trend > 0 ? 'green.500' : trend < 0 ? 'red.500' : 'gray.500'}>
              {trend > 0 ? <FiTrendingUp /> : trend < 0 ? <FiTrendingDown /> : <FiMinus />}
              <Text>{Math.abs(trend)}%</Text>
            </HStack>
          )}
        </HStack>
        <Text fontSize="2xl" fontWeight="bold">{value}</Text>
        <Text fontSize="sm" color="gray.500">{label}</Text>
        {helpText && <Text fontSize="xs" color="gray.400">{helpText}</Text>}
      </CardBody>
    </Card>
  )
}

function GoalCard({ goal }) {
  const statusColor = {
    active: 'green',
    completed: 'blue',
    paused: 'gray'
  }

  return (
    <Card>
      <CardBody>
        <HStack justify="space-between" mb={2}>
          <Text fontWeight="600">{goal.title}</Text>
          <Badge colorScheme={statusColor[goal.status]}>{goal.status}</Badge>
        </HStack>
        <Progress value={goal.progress} colorScheme="brand" borderRadius="full" mb={2} />
        <HStack justify="space-between" fontSize="sm" color="gray.500">
          <Text>{goal.progress}% complete</Text>
          <Text>{goal.description}</Text>
        </HStack>
      </CardBody>
    </Card>
  )
}

function TaskItem({ task, onToggle }) {
  return (
    <HStack 
      p={3} 
      bg="white" 
      rounded="lg" 
      border="1px" 
      borderColor="gray.100"
      _hover={{ borderColor: 'brand.200', boxShadow: 'sm' }}
      cursor="pointer"
      onClick={() => onToggle(task.id)}
    >
      <Box
        w={5}
        h={5}
        rounded="md"
        border="2px"
        borderColor={task.is_completed ? 'green.500' : 'gray.300'}
        bg={task.is_completed ? 'green.500' : 'transparent'}
        display="flex"
        alignItems="center"
        justifyContent="center"
        onClick={(e) => {
          e.stopPropagation()
          onToggle(task.id)
        }}
      >
        {task.is_completed && <FiCheck color="white" size={12} />}
      </Box>
      <VStack align="start" spacing={0} flex={1}>
        <Text 
          fontSize="sm" 
          fontWeight="500" 
          textDecoration={task.is_completed ? 'line-through' : 'none'}
          color={task.is_completed ? 'gray.400' : 'gray.700'}
        >
          {task.title}
        </Text>
        {task.due_date && (
          <HStack spacing={1} fontSize="xs" color="gray.400">
            <FiClock size={10} />
            <Text>{task.due_date}</Text>
          </HStack>
        )}
      </VStack>
      <Badge 
        colorScheme={task.priority === 'high' ? 'red' : task.priority === 'medium' ? 'orange' : 'gray'}
        fontSize="xs"
      >
        {task.priority}
      </Badge>
    </HStack>
  )
}

function RecommendationCard({ rec, onComplete }) {
  const priorityColor = {
    high: 'red',
    medium: 'orange',
    low: 'gray'
  }

  return (
    <Card>
      <CardBody>
        <HStack justify="space-between" mb={2}>
          <Badge colorScheme={priorityColor[rec.priority]}>{rec.priority}</Badge>
          {!rec.is_completed && (
            <Button size="xs" leftIcon={<FiCheck />} onClick={() => onComplete(rec.id)}>
              Done
            </Button>
          )}
        </HStack>
        <Text fontWeight="600" mb={1}>{rec.title}</Text>
        <Text fontSize="sm" color="gray.500">{rec.description}</Text>
      </CardBody>
    </Card>
  )
}

function QuickAction({ icon: Icon, label, to }) {
  return (
    <Link to={to}>
      <VStack
        p={4}
        bg="white"
        rounded="xl"
        border="1px"
        borderColor="gray.100"
        _hover={{ borderColor: 'brand.200', boxShadow: 'md', transform: 'translateY(-2px)' }}
        transition="all 0.2s"
        spacing={2}
      >
        <Box p={3} bg="brand.50" rounded="lg">
          <Icon size={24} color="#F59E0B" />
        </Box>
        <Text fontSize="sm" fontWeight="500">{label}</Text>
      </VStack>
    </Link>
  )
}

function Dashboard() {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState(null)

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      const response = await dashboardAPI.getDashboard()
      setData(response.data)
    } catch (err) {
      console.error('Failed to load dashboard:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleToggleTask = async (taskId) => {
    try {
      await dashboardAPI.toggleTask(taskId)
      loadDashboard()
    } catch (err) {
      console.error('Failed to toggle task:', err)
    }
  }

  const handleCompleteRec = async (recId) => {
    try {
      await dashboardAPI.completeRecommendation(recId)
      loadDashboard()
    } catch (err) {
      console.error('Failed to complete recommendation:', err)
    }
  }

  if (loading) {
    return (
      <Center h="400px">
        <Spinner size="xl" color="brand.500" />
      </Center>
    )
  }

  const overview = data?.overview || {}
  const goals = data?.goals || []
  const tasks = data?.top_recommendations || []
  const recs = data?.recent_activity || []

  return (
    <VStack spacing={6} align="stretch">
      {/* Header */}
      <HStack justify="space-between" align="center">
        <VStack align="start" spacing={0}>
          <Text fontSize="sm" color="gray.500">Good {new Date().getHours() < 12 ? 'morning' : new Date().getHours() < 18 ? 'afternoon' : 'evening'}</Text>
          <Heading size="lg">{user?.full_name || 'User'}</Heading>
        </VStack>
        <Button leftIcon={<FiPlus />}>New Goal</Button>
      </HStack>

      {/* Stats Grid */}
      <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
        <StatCard icon={FiTrendingUp} label="Active Goals" value={overview.active_goals || 0} />
        <StatCard icon={FiCheck} label="Completed" value={overview.completed_goals || 0} />
        <StatCard icon={FiClock} label="Pending Recs" value={overview.pending_recommendations || 0} helpText="This week" />
        <StatCard icon={FiTrendingUp} label="Streak" value={`${overview.streak_days || 0} days`} trend={12} />
      </SimpleGrid>

      {/* Main Grid */}
      <Grid templateColumns={{ base: '1fr', lg: '2fr 1fr' }} gap={6}>
        {/* Left Column */}
        <GridItem>
          <VStack spacing={6} align="stretch">
            {/* Goals */}
            <Card>
              <CardHeader pb={0}>
                <HStack justify="space-between">
                  <Heading size="md">Goals</Heading>
                  <Link to="/goals">
                    <Button variant="link" rightIcon={<FiArrowRight />} size="sm">View all</Button>
                  </Link>
                </HStack>
              </CardHeader>
              <CardBody>
                <VStack spacing={3} align="stretch">
                  {goals.slice(0, 3).map(goal => (
                    <GoalCard key={goal.id} goal={goal} />
                  ))}
                  {goals.length === 0 && (
                    <Text color="gray.500" textAlign="center" py={4}>No goals yet. Create your first goal!</Text>
                  )}
                </VStack>
              </CardBody>
            </Card>

            {/* Tasks */}
            <Card>
              <CardHeader pb={0}>
                <HStack justify="space-between">
                  <Heading size="md">Tasks</Heading>
                  <Link to="/tasks">
                    <Button variant="link" rightIcon={<FiArrowRight />} size="sm">View all</Button>
                  </Link>
                </HStack>
              </CardHeader>
              <CardBody>
                <VStack spacing={2} align="stretch">
                  {tasks.slice(0, 4).map(task => (
                    <TaskItem key={task.id} task={task} onToggle={handleToggleTask} />
                  ))}
                </VStack>
              </CardBody>
            </Card>
          </VStack>
        </GridItem>

        {/* Right Column */}
        <GridItem>
          <VStack spacing={6} align="stretch">
            {/* Quick Actions */}
            <Card>
              <CardHeader pb={0}>
                <Heading size="md">Quick Actions</Heading>
              </CardHeader>
              <CardBody>
                <SimpleGrid columns={3} spacing={3}>
                  <QuickAction icon={FiPlus} label="New Goal" to="/goals" />
                  <QuickAction icon={FiClock} label="Tasks" to="/tasks" />
                  <QuickAction icon={FiTrendingUp} label="Chat" to="/chat" />
                </SimpleGrid>
              </CardBody>
            </Card>

            {/* Recommendations */}
            <Card>
              <CardHeader pb={0}>
                <HStack justify="space-between">
                  <Heading size="md">AI Recommendations</Heading>
                </HStack>
              </CardHeader>
              <CardBody>
                <VStack spacing={3} align="stretch">
                  {recs.slice(0, 3).map(rec => (
                    <RecommendationCard key={rec.id} rec={rec} onComplete={handleCompleteRec} />
                  ))}
                </VStack>
              </CardBody>
            </Card>
          </VStack>
        </GridItem>
      </Grid>
    </VStack>
  )
}

export default Dashboard
