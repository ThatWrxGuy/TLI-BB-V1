import { useState, useEffect } from 'react'
import { Box, VStack, HStack, Text, Heading, Card, CardBody, CardHeader, SimpleGrid, Badge, Stat, StatLabel, StatNumber, StatHelpText, Select, Tabs, TabList, TabPanels, Tab, TabPanel, Table, Thead, Tbody, Tr, Th, Td, Progress } from '@chakra-ui/react'
import { FiUsers, FiTrendingUp, FiDollarSign, FiActivity, FiBarChart2 } from 'react-icons/fi'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { analyticsAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'

const COLORS = ['#F59E0B', '#3B82F6', '#10B981', '#EF4444', '#8B5CF6']

function StatCard({ icon: Icon, label, value, helpText, color }) {
  return (
    <Card>
      <CardBody>
        <HStack justify="space-between">
          <Box p={2} bg={`${color}.50`} rounded="lg">
            <Icon size={20} color={color === 'brand' ? '#F59E0B' : color === 'green' ? '#10B981' : '#3B82F6'} />
          </Box>
        </HStack>
        <Text fontSize="2xl" fontWeight="bold" mt={3}>{value}</Text>
        <Text fontSize="sm" color="gray.500">{label}</Text>
        {helpText && <Text fontSize="xs" color="gray.400">{helpText}</Text>}
      </CardBody>
    </Card>
  )
}

function Analytics() {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('30')
  const [dashboard, setDashboard] = useState(null)
  const [revenue, setRevenue] = useState(null)
  const [usage, setUsage] = useState(null)
  const [retention, setRetention] = useState(null)
  const [funnels, setFunnels] = useState(null)

  useEffect(() => {
    if (user?.role !== 'admin') {
      setLoading(false)
      return
    }
    loadAnalytics()
  }, [user, timeRange])

  const loadAnalytics = async () => {
    setLoading(true)
    try {
      const [dashRes, revRes, usageRes, retRes, funRes] = await Promise.all([
        analyticsAPI.getDashboard(),
        analyticsAPI.getRevenue(),
        analyticsAPI.getUsage(parseInt(timeRange)),
        analyticsAPI.getRetention(),
        analyticsAPI.getFunnels(),
      ])
      setDashboard(dashRes.data)
      setRevenue(revRes.data)
      setUsage(usageRes.data)
      setRetention(retRes.data)
      setFunnels(funRes.data)
    } catch (err) {
      console.error('Failed to load analytics:', err)
    } finally {
      setLoading(false)
    }
  }

  if (user?.role !== 'admin') {
    return (
      <Box p={8} textAlign="center">
        <Text fontSize="4xl">🔒</Text>
        <Text fontSize="xl" fontWeight="bold" mt={4}>Admin Access Required</Text>
        <Text color="gray.500">You need admin privileges to view analytics.</Text>
      </Box>
    )
  }

  return (
    <VStack spacing={6} align="stretch">
      {/* Header */}
      <HStack justify="space-between">
        <Heading size="lg">Analytics</Heading>
        <Select value={timeRange} onChange={(e) => setTimeRange(e.target.value)} w="150px">
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="90">Last 90 days</option>
        </Select>
      </HStack>

      {/* Stats Overview */}
      <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
        <StatCard icon={FiUsers} label="Total Users" value={dashboard?.total_users?.toLocaleString() || 0} color="brand" />
        <StatCard icon={FiActivity} label="Active Users" value={dashboard?.active_users?.toLocaleString() || 0} color="green" />
        <StatCard icon={FiTrendingUp} label="New This Month" value={dashboard?.new_users_this_month?.toLocaleString() || 0} color="blue" />
        <StatCard icon={FiDollarSign} label="MRR" value={`$${revenue?.mrr?.toLocaleString() || 0}`} color="brand" />
      </SimpleGrid>

      {/* Charts */}
      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
        {/* Daily Active Users */}
        <Card>
          <CardHeader>
            <Heading size="sm">Daily Active Users</Heading>
          </CardHeader>
          <CardBody>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={usage?.daily_active_users || []}>
                <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="#F59E0B" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>

        {/* Revenue */}
        <Card>
          <CardHeader>
            <Heading size="sm">Revenue Metrics</Heading>
          </CardHeader>
          <CardBody>
            <SimpleGrid columns={2} spacing={4}>
              <Stat>
                <StatLabel>Monthly Recurring</StatLabel>
                <StatNumber color="brand.500">${revenue?.mrr?.toLocaleString()}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Annual Recurring</StatLabel>
                <StatNumber>${revenue?.arr?.toLocaleString()}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Churn Rate</StatLabel>
                <StatNumber color="red.500">{revenue?.churn_rate}%</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Avg Revenue/User</StatLabel>
                <StatNumber>${revenue?.arpu}</StatNumber>
              </Stat>
            </SimpleGrid>
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* Feature Usage */}
      <Card>
        <CardHeader>
          <Heading size="sm">Feature Usage</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={3} align="stretch">
            {usage?.top_features?.map((feature, i) => (
              <Box key={feature.name}>
                <HStack justify="space-between" mb={1}>
                  <Text fontSize="sm" fontWeight="500">{feature.name}</Text>
                  <Text fontSize="sm" color="gray.500">{feature.usage}%</Text>
                </HStack>
                <Progress value={feature.usage} colorScheme="brand" borderRadius="full" size="sm" />
              </Box>
            ))}
          </VStack>
        </CardBody>
      </Card>

      {/* Funnels */}
      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
        {/* Onboarding Funnel */}
        <Card>
          <CardHeader>
            <Heading size="sm">Onboarding Funnel</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={2} align="stretch">
              {funnels?.onboarding_funnel?.map((step, i) => (
                <HStack key={step.step} justify="space-between">
                  <HStack>
                    <Text fontSize="sm" color="gray.500" w="140px">{step.step}</Text>
                    <Badge colorScheme="brand">{step.percentage}%</Badge>
                  </HStack>
                  <Progress value={step.percentage} colorScheme="green" flex={1} size="sm" borderRadius="full" />
                </HStack>
              ))}
            </VStack>
          </CardBody>
        </Card>

        {/* Retention */}
        <Card>
          <CardHeader>
            <Heading size="sm">User Retention</Heading>
          </CardHeader>
          <CardBody>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={retention?.daily_retention || []}>
                <XAxis dataKey="day" tick={{ fontSize: 10 }} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="retention" fill="#F59E0B" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>
      </SimpleGrid>
    </VStack>
  )
}

export default Analytics
