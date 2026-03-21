import { useState, useEffect } from 'react'
import { Box, VStack, HStack, Text, Heading, Card, CardBody, CardHeader, SimpleGrid, Badge, Button, Progress, Icon, Stat, StatLabel, StatNumber, StatHelpText, Tabs, TabList, TabPanels, Tab, TabPanel, Table, Thead, Tbody, Tr, Th, Td, Avatar, Flex } from '@chakra-ui/react'
import { FiTrendingUp, FiAward, FiZap, FiTarget, FiCalendar, FiBarChart2, FiChevronRight, FiStar } from 'react-icons/fi'
import { LineChart, Line, BarChart, Bar, AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { userAnalyticsAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'

function ActivityTimeline() {
  const [data, setData] = useState(null)

  useEffect(() => {
    userAnalyticsAPI.getActivity(30).then(r => setData(r.data)).catch(console.error)
  }, [])

  return (
    <Card>
      <CardHeader>
        <Heading size="sm">Activity Timeline</Heading>
      </CardHeader>
      <CardBody>
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={data?.days || []}>
            <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={(v) => v.slice(5)} />
            <YAxis />
            <Tooltip />
            <Area type="monotone" dataKey="tasks_completed" stackId="1" stroke="#F59E0B" fill="#FDE68A" />
            <Area type="monotone" dataKey="goals_completed" stackId="2" stroke="#3B82F6" fill="#93C5FD" />
          </AreaChart>
        </ResponsiveContainer>
        {data && (
          <HStack justify="space-around" mt={4}>
            <VStack><Text fontSize="xl" fontWeight="bold">{data.total_tasks_completed}</Text><Text fontSize="xs" color="gray.500">Tasks Done</Text></VStack>
            <VStack><Text fontSize="xl" fontWeight="bold">{data.total_goals_completed}</Text><Text fontSize="xs" color="gray.500">Goals Done</Text></VStack>
            <VStack><Text fontSize="xl" fontWeight="bold">{Math.round(data.total_minutes_active / 60)}h</Text><Text fontSize="xs" color="gray.500">Active</Text></VStack>
          </HStack>
        )}
      </CardBody>
    </Card>
  )
}

function StreakCard() {
  const [streaks, setStreaks] = useState(null)

  useEffect(() => {
    userAnalyticsAPI.getStreaks().then(r => setStreaks(r.data)).catch(console.error)
  }, [])

  return (
    <Card bg="linear-gradient(135deg, #F59E0B 0%, #D97706 100%)" color="white">
      <CardBody>
        <HStack justify="space-between" align="start">
          <VStack align="start" spacing={1}>
            <HStack><Icon as={FiZap} /><Text fontSize="sm">Current Streak</Text></HStack>
            <Text fontSize="4xl" fontWeight="bold">{streaks?.current_streak || 0}</Text>
            <Text fontSize="sm" opacity={0.8}>days</Text>
          </VStack>
          <VStack align="end" spacing={1}>
            <Text fontSize="sm" opacity={0.8}>Longest</Text>
            <Text fontSize="2xl" fontWeight="bold">{streaks?.longest_streak || 0}</Text>
            <Text fontSize="xs" opacity={0.8}>days</Text>
          </VStack>
        </HStack>
        <Box mt={4}>
          <Text fontSize="xs" mb={2}>Milestones</Text>
          <HStack spacing={2} flexWrap="wrap">
            {streaks?.milestones?.map(m => (
              <Badge key={m.days} colorScheme={m.achieved ? 'green' : 'gray'} variant={m.achieved ? 'solid' : 'outline'}>
                {m.days}d {m.achieved ? '✓' : '○'}
              </Badge>
            ))}
          </HStack>
        </Box>
      </CardBody>
    </Card>
  )
}

function AchievementsCard() {
  const [achievements, setAchievements] = useState(null)

  useEffect(() => {
    userAnalyticsAPI.getAchievements().then(r => setAchievements(r.data)).catch(console.error)
  }, [])

  return (
    <Card>
      <CardHeader>
        <HStack justify="space-between">
          <Heading size="sm">Achievements</Heading>
          <Badge colorScheme="brand">{achievements?.total_earned || 0}/{achievements?.total_available || 0}</Badge>
        </HStack>
      </CardHeader>
      <CardBody>
        <SimpleGrid columns={4} spacing={2}>
          {achievements?.achievements?.map(a => (
            <VStack key={a.id} spacing={1} p={2} borderRadius="md" bg={a.is_earned ? 'brand.50' : 'gray.50'}>
              <Text fontSize="2xl">{a.icon}</Text>
              <Text fontSize="xs" textAlign="center" noOfLines={2}>{a.name}</Text>
              {!a.is_earned && a.progress && (
                <Progress value={a.progress} size="xs" colorScheme="brand" w="full" />
              )}
            </VStack>
          ))}
        </SimpleGrid>
      </CardBody>
    </Card>
  )
}

function InsightsCard() {
  const [insights, setInsights] = useState(null)

  useEffect(() => {
    userAnalyticsAPI.getInsights().then(r => setInsights(r.data)).catch(console.error)
  }, [])

  const getIcon = (type) => {
    switch (type) {
      case 'tip': return '💡'
      case 'warning': return '⚠️'
      case 'achievement': return '🎉'
      case 'suggestion': return '✨'
      default: return '📌'
    }
  }

  const getColor = (type) => {
    switch (type) {
      case 'tip': return 'blue'
      case 'warning': return 'orange'
      case 'achievement': return 'green'
      case 'suggestion': return 'purple'
      default: return 'gray'
    }
  }

  return (
    <Card>
      <CardHeader>
        <Heading size="sm">Insights</Heading>
      </CardHeader>
      <CardBody>
        <VStack spacing={3} align="stretch">
          {insights?.insights?.map(insight => (
            <HStack key={insight.id} p={3} borderRadius="md" bg={`${getColor(insight.type)}.50`} align="start">
              <Text fontSize="xl">{getIcon(insight.type)}</Text>
              <VStack align="start" spacing={0} flex={1}>
                <Text fontWeight="600" fontSize="sm">{insight.title}</Text>
                <Text fontSize="xs" color="gray.600">{insight.message}</Text>
              </VStack>
            </HStack>
          ))}
        </VStack>
      </CardBody>
    </Card>
  )
}

function WeeklyReport() {
  const [report, setReport] = useState(null)

  useEffect(() => {
    userAnalyticsAPI.getWeeklyReport().then(r => setReport(r.data)).catch(console.error)
  }, [])

  return (
    <Card>
      <CardHeader>
        <HStack justify="space-between">
          <Heading size="sm">Weekly Report</Heading>
          <Text fontSize="xs" color="gray.500">{report?.week_start} - {report?.week_end}</Text>
        </HStack>
      </CardHeader>
      <CardBody>
        <SimpleGrid columns={3} spacing={4} mb={4}>
          <Stat size="sm">
            <StatLabel fontSize="xs">Goals Done</StatLabel>
            <StatNumber fontSize="xl">{report?.summary?.goals_completed || 0}</StatNumber>
          </Stat>
          <Stat size="sm">
            <StatLabel fontSize="xs">Tasks Done</StatLabel>
            <StatNumber fontSize="xl">{report?.summary?.tasks_completed || 0}</StatNumber>
          </Stat>
          <Stat size="sm">
            <StatLabel fontSize="xs">Days Active</StatLabel>
            <StatNumber fontSize="xl">{report?.summary?.days_active || 0}/7</StatNumber>
          </Stat>
        </SimpleGrid>
        
        <Text fontWeight="600" fontSize="sm" mb={2}>Accomplishments</Text>
        <VStack align="stretch" spacing={1} mb={4}>
          {report?.accomplishments?.map((acc, i) => (
            <HStack key={i} fontSize="sm"><Text>✓</Text><Text>{acc}</Text></HStack>
          ))}
        </VStack>
        
        <Text fontWeight="600" fontSize="sm" mb={2}>Next Week Suggestions</Text>
        <VStack align="stretch" spacing={1}>
          {report?.next_week_suggestions?.map((sug, i) => (
            <HStack key={i} fontSize="sm"><Icon as={FiChevronRight} /><Text>{sug}</Text></HStack>
          ))}
        </VStack>
      </CardBody>
    </Card>
  )
}

function BenchmarkCard() {
  const [benchmark, setBenchmark] = useState(null)

  useEffect(() => {
    userAnalyticsAPI.getBenchmark().then(r => setBenchmark(r.data)).catch(console.error)
  }, [])

  return (
    <Card>
      <CardHeader>
        <HStack justify="space-between">
          <Heading size="sm">Compare to Average</Heading>
          <Badge colorScheme="green">{benchmark?.percentile?.toFixed(0)}%</Badge>
        </HStack>
      </CardHeader>
      <CardBody>
        <VStack spacing={3} align="stretch">
          {benchmark?.comparison?.map((item, i) => (
            <HStack key={i} justify="space-between">
              <VStack align="start" spacing={0}>
                <Text fontSize="sm" fontWeight="500">{item.metric}</Text>
                <HStack>
                  <Text fontSize="xs" color="brand.500" fontWeight="bold">{item.you}</Text>
                  <Text fontSize="xs" color="gray.400">vs</Text>
                  <Text fontSize="xs" color="gray.500">{item.average}</Text>
                </HStack>
              </VStack>
              <Badge colorScheme={item.status === 'above' ? 'green' : 'red'} variant="subtle">
                {item.status === 'above' ? '↑ Above' : '↓ Below'}
              </Badge>
            </HStack>
          ))}
        </VStack>
      </CardBody>
    </Card>
  )
}

function ProgressCharts() {
  const [progress, setProgress] = useState(null)

  useEffect(() => {
    userAnalyticsAPI.getProgress().then(r => setProgress(r.data)).catch(console.error)
  }, [])

  return (
    <Card>
      <CardHeader>
        <Heading size="sm">Goal Progress Over Time</Heading>
      </CardHeader>
      <CardBody>
        <ResponsiveContainer width="100%" height={150}>
          <LineChart data={progress?.goal_progress || []}>
            <XAxis dataKey="week" tick={{ fontSize: 10 }} tickFormatter={(v) => v.slice(5)} />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="goals_active" stroke="#F59E0B" strokeWidth={2} name="Active" />
            <Line type="monotone" dataKey="goals_completed" stroke="#10B981" strokeWidth={2} name="Completed" />
          </LineChart>
        </ResponsiveContainer>
      </CardBody>
    </Card>
  )
}

function SummaryCard() {
  const [summary, setSummary] = useState(null)

  useEffect(() => {
    userAnalyticsAPI.getSummary().then(r => setSummary(r.data)).catch(console.error)
  }, [])

  return (
    <Card bg="gray.50">
      <CardBody>
        <HStack justify="space-between" flexWrap="wrap" gap={4}>
          <VStack><Text fontSize="2xl" fontWeight="bold">{summary?.total_goals || 0}</Text><Text fontSize="xs" color="gray.500">Total Goals</Text></VStack>
          <VStack><Text fontSize="2xl" fontWeight="bold">{summary?.completed_goals || 0}</Text><Text fontSize="xs" color="gray.500">Completed</Text></VStack>
          <VStack><Text fontSize="2xl" fontWeight="bold">{summary?.total_tasks || 0}</Text><Text fontSize="xs" color="gray.500">Total Tasks</Text></VStack>
          <VStack><Text fontSize="2xl" fontWeight="bold">{summary?.current_streak || 0}</Text><Text fontSize="xs" color="gray.500">Day Streak</Text></VStack>
          <VStack><Text fontSize="2xl" fontWeight="bold">{summary?.achievements_earned || 0}</Text><Text fontSize="xs" color="gray.500">Badges</Text></VStack>
        </HStack>
      </CardBody>
    </Card>
  )
}

export default function UserAnalytics() {
  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        <Heading size="lg">Your Analytics</Heading>
        
        <SummaryCard />
        
        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
          <StreakCard />
          <ProgressCharts />
        </SimpleGrid>
        
        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
          <ActivityTimeline />
          <AchievementsCard />
        </SimpleGrid>
        
        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
          <InsightsCard />
          <WeeklyReport />
        </SimpleGrid>
        
        <BenchmarkCard />
      </VStack>
    </Box>
  )
}
