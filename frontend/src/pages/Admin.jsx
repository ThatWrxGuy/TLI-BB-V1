import { useState, useEffect } from 'react'
import { Box, VStack, HStack, Text, Heading, Button, Card, CardBody, CardHeader, SimpleGrid, Badge, Table, Thead, Tbody, Tr, Th, Td, Stat, StatLabel, StatNumber, StatHelpText, Tabs, TabList, TabPanels, Tab, TabPanel, Spinner, Center, Input, InputGroup, InputLeftElement } from '@chakra-ui/react'
import { FiSearch, FiUsers, FiDollarSign, FiActivity, FiSettings } from 'react-icons/fi'
import { adminAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'

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

function Admin() {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [health, setHealth] = useState(null)

  useEffect(() => {
    if (user?.role !== 'admin') {
      setLoading(false)
      return
    }
    loadAdmin()
  }, [user])

  const loadAdmin = async () => {
    try {
      const [statsRes, usersRes, healthRes] = await Promise.all([
        adminAPI.getStats(),
        adminAPI.getUsers({ page: 1, per_page: 10 }),
        adminAPI.getSystemHealth()
      ])
      setStats(statsRes.data)
      setUsers(usersRes.data.users || [])
      setHealth(healthRes.data)
    } catch (err) {
      console.error('Failed to load admin:', err)
    } finally {
      setLoading(false)
    }
  }

  if (user?.role !== 'admin') {
    return (
      <Center h="400px">
        <VStack spacing={4}>
          <Text fontSize="4xl">🔒</Text>
          <Text fontSize="xl" fontWeight="bold">Access Denied</Text>
          <Text color="gray.500">You don't have admin access</Text>
        </VStack>
      </Center>
    )
  }

  if (loading) {
    return (
      <Center h="400px">
        <Spinner size="xl" color="brand.500" />
      </Center>
    )
  }

  return (
    <VStack spacing={6} align="stretch">
      <Heading size="lg">Admin Dashboard</Heading>

      {/* Stats */}
      <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
        <StatCard icon={FiUsers} label="Total Users" value={stats?.total_users || 0} color="brand" />
        <StatCard icon={FiUsers} label="Active (30d)" value={stats?.active_users_30d || 0} color="green" />
        <StatCard icon={FiUsers} label="New (30d)" value={stats?.new_users_30d || 0} color="blue" />
        <StatCard icon={FiDollarSign} label="MRR" value={`$${stats?.mrr?.toLocaleString() || 0}`} color="brand" />
      </SimpleGrid>

      {/* Tabs */}
      <Tabs>
        <TabList>
          <Tab>Users</Tab>
          <Tab>Revenue</Tab>
          <Tab>System</Tab>
          <Tab>Settings</Tab>
        </TabList>

        <TabPanels>
          {/* Users */}
          <TabPanel px={0}>
            <Card>
              <CardHeader>
                <HStack justify="space-between">
                  <Heading size="sm">All Users</Heading>
                  <InputGroup maxW="300px">
                    <InputLeftElement><FiSearch /></InputLeftElement>
                    <Input placeholder="Search users..." />
                  </InputGroup>
                </HStack>
              </CardHeader>
              <CardBody>
                <Table variant="simple" size="sm">
                  <Thead>
                    <Tr>
                      <Th>User</Th>
                      <Th>Role</Th>
                      <Th>Plan</Th>
                      <Th>Status</Th>
                      <Th>Joined</Th>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {users.map((u) => (
                      <Tr key={u.id}>
                        <Td>
                          <VStack align="start" spacing={0}>
                            <Text fontWeight="500">{u.full_name}</Text>
                            <Text fontSize="xs" color="gray.500">{u.email}</Text>
                          </VStack>
                        </Td>
                        <Td><Badge>{u.role}</Badge></Td>
                        <Td><Badge colorScheme="brand">{u.plan}</Badge></Td>
                        <Td><Badge colorScheme={u.status === 'active' ? 'green' : 'gray'}>{u.status}</Badge></Td>
                        <Td>{new Date(u.created_at).toLocaleDateString()}</Td>
                      </Tr>
                    ))}
                  </Tbody>
                </Table>
              </CardBody>
            </Card>
          </TabPanel>

          {/* Revenue */}
          <TabPanel px={0}>
            <Card>
              <CardHeader>
                <Heading size="sm">Revenue Metrics</Heading>
              </CardHeader>
              <CardBody>
                <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
                  <Stat>
                    <StatLabel>Total Revenue</StatLabel>
                    <StatNumber>${stats?.total_revenue?.toLocaleString()}</StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>MRR</StatLabel>
                    <StatNumber>${stats?.mrr?.toLocaleString()}</StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>ARR</StatLabel>
                    <StatNumber>${stats?.arr?.toLocaleString()}</StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>Churn Rate</StatLabel>
                    <StatNumber>{stats?.churn_rate}%</StatNumber>
                  </Stat>
                </SimpleGrid>
              </CardBody>
            </Card>
          </TabPanel>

          {/* System */}
          <TabPanel px={0}>
            <Card>
              <CardHeader>
                <Heading size="sm">System Health</Heading>
              </CardHeader>
              <CardBody>
                <HStack spacing={4} mb={4}>
                  <Badge colorScheme={health?.status === 'healthy' ? 'green' : 'red'} fontSize="md" p={2}>
                    {health?.status?.toUpperCase()}
                  </Badge>
                  <Text>Uptime: {Math.floor(health?.uptime / 3600)}h</Text>
                  <Text>API: {health?.api_response_time}ms</Text>
                </HStack>
                <SimpleGrid columns={2} spacing={4}>
                  {Object.entries(health?.external_services || {}).map(([service, status]) => (
                    <HStack key={service} justify="space-between" p={3} bg="gray.50" rounded="lg">
                      <Text textTransform="capitalize">{service}</Text>
                      <Badge colorScheme={status === 'healthy' ? 'green' : 'red'}>{status}</Badge>
                    </HStack>
                  ))}
                </SimpleGrid>
              </CardBody>
            </Card>
          </TabPanel>

          {/* Settings */}
          <TabPanel px={0}>
            <Card>
              <CardHeader>
                <Heading size="sm">Platform Settings</Heading>
              </CardHeader>
              <CardBody>
                <VStack spacing={4} align="stretch">
                  <HStack justify="space-between">
                    <Text>Allow Signups</Text>
                    <Badge colorScheme="green">Enabled</Badge>
                  </HStack>
                  <HStack justify="space-between">
                    <Text>Email Verification Required</Text>
                    <Badge colorScheme="green">Enabled</Badge>
                  </HStack>
                  <HStack justify="space-between">
                    <Text>Maintenance Mode</Text>
                    <Badge colorScheme="gray">Disabled</Badge>
                  </HStack>
                </VStack>
              </CardBody>
            </Card>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </VStack>
  )
}

export default Admin
