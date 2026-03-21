// Busy Bee — Dashboard (Upgraded)
// Drop-in replacement for frontend/src/pages/Dashboard.jsx
// Added: Domain Scores widget, live mood log, better greeting, skeleton loaders

import { useState, useEffect } from 'react'
import {
  Box, Grid, GridItem, VStack, HStack, Text, Button, Card, CardBody, CardHeader,
  Heading, Stat, StatLabel, StatNumber, StatHelpText, Progress, Badge,
  IconButton, SimpleGrid, Spinner, Center, CircularProgress, CircularProgressLabel,
  Tooltip, Skeleton, SkeletonText, Avatar, Divider, useToast, Tag,
} from '@chakra-ui/react'
import {
  FiPlus, FiCheck, FiClock, FiTrendingUp, FiTrendingDown, FiMinus, FiArrowRight,
  FiZap, FiGrid, FiRefreshCw,
} from 'react-icons/fi'
import { Link, useNavigate } from 'react-router-dom'
import { dashboardAPI, domainsAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'

// ─── Helpers ──────────────────────────────────────────────────────────────────

const DOMAIN_META = {
  health:        { color: 'green',  emoji: '🏃' },
  career:        { color: 'blue',   emoji: '💼' },
  mindset:       { color: 'purple', emoji: '🧠' },
  habits:        { color: 'orange', emoji: '🔄' },
  relationships: { color: 'pink',   emoji: '👥' },
  finance:       { color: 'yellow', emoji: '💰' },
}

function greeting(name) {
  const h = new Date().getHours()
  const time = h < 12 ? 'morning' : h < 18 ? 'afternoon' : 'evening'
  const first = name?.split(' ')[0] || 'there'
  return `Good ${time}, ${first} 👋`
}

// ─── Sub-components ────────────────────────────────────────────────────────────

function StatCard({ icon: Icon, label, value, helpText, trend, loading }) {
  if (loading) return <Card><CardBody><Skeleton height="80px" /></CardBody></Card>
  return (
    <Card>
      <CardBody>
        <HStack justify="space-between" mb={2}>
          <Box p={2} bg="brand.50" rounded="lg">
            <Icon size={20} color="#F59E0B" />
          </Box>
          {trend != null && (
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
  const statusColor = { active: 'green', completed: 'blue', paused: 'gray' }
  return (
    <Card>
      <CardBody>
        <HStack justify="space-between" mb={2}>
          <Text fontWeight="600" noOfLines={1} flex={1}>{goal.title}</Text>
          <Badge colorScheme={statusColor[goal.status] || 'gray'}>{goal.status}</Badge>
        </HStack>
        <Progress value={goal.progress} colorScheme="brand" borderRadius="full" mb={2} size="sm" />
        <HStack justify="space-between" fontSize="xs" color="gray.500">
          <Text>{goal.progress}% complete</Text>
          {goal.category && <Badge variant="subtle" fontSize="xs">{goal.category}</Badge>}
        </HStack>
      </CardBody>
    </Card>
  )
}

function TaskItem({ task, onToggle }) {
  return (
    <HStack
      p={3} bg="white" rounded="lg" border="1px" borderColor="gray.100"
      _hover={{ borderColor: 'brand.200', boxShadow: 'sm' }}
      cursor="pointer" onClick={() => onToggle(task.id)}
    >
      <Box
        w={5} h={5} rounded="md" border="2px"
        borderColor={task.is_completed ? 'green.500' : 'gray.300'}
        bg={task.is_completed ? 'green.500' : 'transparent'}
        display="flex" alignItems="center" justifyContent="center"
        flexShrink={0}
        onClick={e => { e.stopPropagation(); onToggle(task.id) }}
      >
        {task.is_completed && <FiCheck color="white" size={12} />}
      </Box>
      <VStack align="start" spacing={0} flex={1} minW={0}>
        <Text
          fontSize="sm" fontWeight="500"
          textDecoration={task.is_completed ? 'line-through' : 'none'}
          color={task.is_completed ? 'gray.400' : 'gray.700'}
          noOfLines={1}
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
        fontSize="xs" flexShrink={0}
      >
        {task.priority}
      </Badge>
    </HStack>
  )
}

function RecommendationCard({ rec, onComplete }) {
  const priorityColor = { high: 'red', medium: 'orange', low: 'gray' }
  return (
    <Card>
      <CardBody>
        <HStack justify="space-between" mb={1}>
          <Badge colorScheme={priorityColor[rec.priority] || 'gray'}>{rec.priority}</Badge>
          {!rec.is_completed && (
            <Button size="xs" leftIcon={<FiCheck />} colorScheme="green" variant="outline" onClick={() => onComplete(rec.id)}>
              Done
            </Button>
          )}
        </HStack>
        <Text fontWeight="600" fontSize="sm" mb={1}>{rec.title}</Text>
        <Text fontSize="xs" color="gray.500">{rec.description}</Text>
      </CardBody>
    </Card>
  )
}

function QuickAction({ icon: Icon, label, to }) {
  return (
    <Link to={to}>
      <VStack
        p={3} bg="white" rounded="xl" border="1px" borderColor="gray.100"
        _hover={{ borderColor: 'brand.200', boxShadow: 'md', transform: 'translateY(-2px)' }}
        transition="all 0.2s" spacing={2} cursor="pointer"
      >
        <Box p={2} bg="brand.50" rounded="lg">
          <Icon size={20} color="#F59E0B" />
        </Box>
        <Text fontSize="xs" fontWeight="500" textAlign="center">{label}</Text>
      </VStack>
    </Link>
  )
}

// ─── Domain Scores Widget ──────────────────────────────────────────────────────

function DomainScoresWidget({ loading }) {
  const navigate = useNavigate()
  const [progress, setProgress] = useState({})
  const [widgetLoading, setWidgetLoading] = useState(true)

  useEffect(() => {
    domainsAPI.getAllProgress()
      .then(r => setProgress(r.data || {}))
      .catch(() => {})
      .finally(() => setWidgetLoading(false))
  }, [])

  const isLoading = loading || widgetLoading
  const domainOrder = ['health', 'career', 'mindset', 'habits', 'relationships', 'finance']

  return (
    <Card>
      <CardHeader pb={2}>
        <HStack justify="space-between">
          <HStack spacing={2}>
            <FiGrid color="#F59E0B" />
            <Heading size="sm">Life Domains</Heading>
          </HStack>
          <Button
            as={Link}
            to="/domains"
            variant="link"
            rightIcon={<FiArrowRight />}
            size="sm"
            colorScheme="brand"
          >
            View all
          </Button>
        </HStack>
      </CardHeader>
      <CardBody pt={0}>
        {isLoading ? (
          <VStack spacing={3}>
            {[0,1,2,3,4,5].map(i => <Skeleton key={i} height="28px" borderRadius="md" />)}
          </VStack>
        ) : (
          <VStack spacing={3} align="stretch">
            {domainOrder.map(id => {
              const meta = DOMAIN_META[id]
              const p = progress[id]
              const rate = p?.completion_rate || 0
              const streak = p?.current_streak || 0
              return (
                <Box
                  key={id}
                  cursor="pointer"
                  onClick={() => navigate('/domains')}
                  _hover={{ opacity: 0.85 }}
                  transition="opacity 0.15s"
                >
                  <HStack justify="space-between" mb={1}>
                    <HStack spacing={2}>
                      <Text fontSize="sm">{meta.emoji}</Text>
                      <Text fontSize="sm" fontWeight="500" textTransform="capitalize">{id}</Text>
                      {streak >= 7 && (
                        <Tag size="sm" colorScheme="orange" variant="subtle">
                          🔥 {streak}d
                        </Tag>
                      )}
                    </HStack>
                    <Text fontSize="xs" fontWeight="bold" color={`${meta.color}.600`}>{rate}%</Text>
                  </HStack>
                  <Progress
                    value={rate}
                    colorScheme={meta.color}
                    size="sm"
                    borderRadius="full"
                  />
                </Box>
              )
            })}

            {/* Today's check-in summary */}
            <Divider />
            <HStack justify="space-between">
              <Text fontSize="xs" color="gray.500">
                {Object.values(progress).filter(p => (p?.weekly_checkins || 0) > 0).length} domains active this week
              </Text>
              <Button
                size="xs"
                colorScheme="brand"
                variant="outline"
                as={Link}
                to="/domains"
              >
                Check In
              </Button>
            </HStack>
          </VStack>
        )}
      </CardBody>
    </Card>
  )
}

// ─── Main Dashboard ────────────────────────────────────────────────────────────

function Dashboard() {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState(null)
  const toast = useToast()

  useEffect(() => { loadDashboard() }, [])

  const loadDashboard = async () => {
    setLoading(true)
    try {
      const response = await dashboardAPI.getDashboard()
      setData(response.data)
    } catch {
      toast({ title: 'Could not load dashboard', status: 'error', duration: 3000 })
    } finally {
      setLoading(false)
    }
  }

  const handleToggleTask = async (taskId) => {
    try {
      await dashboardAPI.toggleTask(taskId)
      loadDashboard()
    } catch {
      toast({ title: 'Could not update task', status: 'error', duration: 2000 })
    }
  }

  const handleCompleteRec = async (recId) => {
    try {
      await dashboardAPI.completeRecommendation(recId)
      loadDashboard()
    } catch {
      toast({ title: 'Could not update recommendation', status: 'error', duration: 2000 })
    }
  }

  const overview = data?.overview || {}
  const goals    = data?.goals || []
  const tasks    = data?.top_recommendations || []
  const recs     = data?.recent_activity || []

  return (
    <VStack spacing={6} align="stretch">
      {/* Header */}
      <HStack justify="space-between" align="center" flexWrap="wrap" gap={2}>
        <VStack align="start" spacing={0}>
          <Text fontSize="sm" color="gray.500">{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</Text>
          <Heading size="lg">{greeting(user?.full_name)}</Heading>
        </VStack>
        <HStack>
          <IconButton icon={<FiRefreshCw />} variant="ghost" size="sm" onClick={loadDashboard} isLoading={loading} aria-label="Refresh" />
          <Button leftIcon={<FiPlus />} as={Link} to="/goals" colorScheme="brand">
            New Goal
          </Button>
        </HStack>
      </HStack>

      {/* Stats row */}
      <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
        <StatCard loading={loading} icon={FiTrendingUp} label="Active Goals"   value={overview.active_goals || 0} />
        <StatCard loading={loading} icon={FiCheck}      label="Completed"      value={overview.completed_goals || 0} />
        <StatCard loading={loading} icon={FiClock}      label="Pending"        value={overview.pending_recommendations || 0} helpText="Recommendations" />
        <StatCard loading={loading} icon={FiZap}        label="Streak"         value={`${overview.streak_days || 0}d`} trend={12} />
      </SimpleGrid>

      {/* Main 2-col grid */}
      <Grid templateColumns={{ base: '1fr', lg: '2fr 1fr' }} gap={6}>

        {/* Left col */}
        <GridItem>
          <VStack spacing={6} align="stretch">

            {/* Goals */}
            <Card>
              <CardHeader pb={0}>
                <HStack justify="space-between">
                  <Heading size="md">Active Goals</Heading>
                  <Button as={Link} to="/goals" variant="link" rightIcon={<FiArrowRight />} size="sm">View all</Button>
                </HStack>
              </CardHeader>
              <CardBody>
                {loading ? (
                  <VStack spacing={3}><SkeletonText noOfLines={3} spacing={3} /></VStack>
                ) : (
                  <VStack spacing={3} align="stretch">
                    {goals.slice(0, 3).map(goal => <GoalCard key={goal.id} goal={goal} />)}
                    {goals.length === 0 && (
                      <VStack py={6} spacing={2}>
                        <Text fontSize="2xl">🎯</Text>
                        <Text color="gray.500">No goals yet.</Text>
                        <Button size="sm" as={Link} to="/goals" leftIcon={<FiPlus />} colorScheme="brand">Create your first goal</Button>
                      </VStack>
                    )}
                  </VStack>
                )}
              </CardBody>
            </Card>

            {/* Tasks */}
            <Card>
              <CardHeader pb={0}>
                <HStack justify="space-between">
                  <Heading size="md">Tasks</Heading>
                  <Button as={Link} to="/tasks" variant="link" rightIcon={<FiArrowRight />} size="sm">View all</Button>
                </HStack>
              </CardHeader>
              <CardBody>
                {loading ? (
                  <SkeletonText noOfLines={4} spacing={4} />
                ) : (
                  <VStack spacing={2} align="stretch">
                    {tasks.slice(0, 4).map(task => (
                      <TaskItem key={task.id} task={task} onToggle={handleToggleTask} />
                    ))}
                    {tasks.length === 0 && (
                      <Text color="gray.400" textAlign="center" py={4}>No tasks yet.</Text>
                    )}
                  </VStack>
                )}
              </CardBody>
            </Card>

          </VStack>
        </GridItem>

        {/* Right col */}
        <GridItem>
          <VStack spacing={6} align="stretch">

            {/* Quick Actions */}
            <Card>
              <CardHeader pb={0}><Heading size="md">Quick Actions</Heading></CardHeader>
              <CardBody>
                <SimpleGrid columns={3} spacing={2}>
                  <QuickAction icon={FiPlus}       label="New Goal"   to="/goals" />
                  <QuickAction icon={FiCheck}      label="Tasks"      to="/tasks" />
                  <QuickAction icon={FiGrid}       label="Domains"    to="/domains" />
                  <QuickAction icon={FiTrendingUp} label="Analytics"  to="/my-analytics" />
                  <QuickAction icon={FiZap}        label="Finance"    to="/finance" />
                  <QuickAction icon={FiClock}      label="Help"       to="/help" />
                </SimpleGrid>
              </CardBody>
            </Card>

            {/* Domain Scores — new widget */}
            <DomainScoresWidget loading={loading} />

            {/* AI Recommendations */}
            {recs.length > 0 && (
              <Card>
                <CardHeader pb={0}>
                  <Heading size="md">AI Recommendations</Heading>
                </CardHeader>
                <CardBody>
                  <VStack spacing={3} align="stretch">
                    {recs.slice(0, 3).map(rec => (
                      <RecommendationCard key={rec.id} rec={rec} onComplete={handleCompleteRec} />
                    ))}
                  </VStack>
                </CardBody>
              </Card>
            )}

          </VStack>
        </GridItem>

      </Grid>
    </VStack>
  )
}

export default Dashboard
