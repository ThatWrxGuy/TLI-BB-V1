import { useState, useEffect } from 'react'
import { Box, VStack, HStack, Text, Heading, Button, Card, CardBody, CardHeader, SimpleGrid, Badge, Table, Thead, Tbody, Tr, Th, Td, Stat, StatLabel, StatNumber, StatHelpText, Progress, Spinner, Center, IconButton } from '@chakra-ui/react'
import { FiPlus, FiTrash2, FiRefreshCw, FiTrendingUp, FiTrendingDown, FiCreditCard } from 'react-icons/fi'
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts'
import { financeAPI } from '../services/api'

const COLORS = ['#F59E0B', '#3B82F6', '#10B981', '#EF4444', '#8B5CF6']

function Finance() {
  const [loading, setLoading] = useState(true)
  const [accounts, setAccounts] = useState([])
  const [insights, setInsights] = useState(null)
  const [transactions, setTransactions] = useState([])

  useEffect(() => {
    loadFinance()
  }, [])

  const loadFinance = async () => {
    try {
      const [accountsRes, insightsRes, transRes] = await Promise.all([
        financeAPI.getAccounts(),
        financeAPI.getInsights(30),
        financeAPI.getTransactions({ limit: 10 })
      ])
      setAccounts(accountsRes.data.accounts || [])
      setInsights(insightsRes.data)
      setTransactions(transactionsRes.data.transactions || [])
    } catch (err) {
      console.error('Failed to load finance:', err)
    } finally {
      setLoading(false)
    }
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
      <HStack justify="space-between">
        <Heading size="lg">Finance</Heading>
        <Button leftIcon={<FiPlus />} colorScheme="brand">Link Account</Button>
      </HStack>

      {/* Net Worth */}
      <Card bg="linear-gradient(135deg, #F59E0B 0%, #EA580C 100%)" color="white">
        <CardBody>
          <HStack justify="space-between">
            <VStack align="start" spacing={1}>
              <Text opacity={0.8}>Net Worth</Text>
              <Text fontSize="4xl" fontWeight="bold">$12,543.67</Text>
              <HStack>
                <FiTrendingUp />
                <Text>+3.2% this month</Text>
              </HStack>
            </VStack>
            <Box p={4} bg="whiteAlpha.200" rounded="xl">
              <FiCreditCard size={40} />
            </Box>
          </HStack>
        </CardBody>
      </Card>

      {/* Stats */}
      <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
        <Card>
          <CardBody>
            <Stat>
              <StatLabel>Total Income</StatLabel>
              <StatNumber color="green.500">${insights?.total_income?.toLocaleString() || '0'}</StatNumber>
            </Stat>
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <Stat>
              <StatLabel>Total Spending</StatLabel>
              <StatNumber color="red.500">${insights?.total_spending?.toLocaleString() || '0'}</StatNumber>
            </Stat>
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <Stat>
              <StatLabel>Avg Daily</StatLabel>
              <StatNumber>${insights?.average_daily_spending?.toFixed(2) || '0'}</StatNumber>
            </Stat>
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <Stat>
              <StatLabel>Net Flow</StatLabel>
              <StatNumber color={insights?.net_flow >= 0 ? 'green.500' : 'red.500'}>
                ${insights?.net_flow?.toLocaleString() || '0'}
              </StatNumber>
            </Stat>
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* Spending by Category */}
      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
        <Card>
          <CardHeader>
            <Heading size="sm">Spending by Category</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={3} align="stretch">
              {insights?.spending_by_category?.map((cat, i) => (
                <HStack key={cat.category} justify="space-between">
                  <HStack>
                    <Text fontSize="xl">{cat.icon}</Text>
                    <Text fontWeight="500" textTransform="capitalize">{cat.category}</Text>
                  </HStack>
                  <VStack align="end" spacing={0}>
                    <Text fontWeight="600">${cat.amount?.toFixed(2)}</Text>
                    <Text fontSize="xs" color="gray.500">{cat.percentage}%</Text>
                  </VStack>
                </HStack>
              ))}
            </VStack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="sm">Insights</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={3} align="stretch">
              {insights?.insights?.map((insight, i) => (
                <HStack key={i} p={3} bg="brand.50" rounded="lg" spacing={3}>
                  <Text>{insight}</Text>
                </HStack>
              ))}
            </VStack>
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* Recent Transactions */}
      <Card>
        <CardHeader>
          <Heading size="sm">Recent Transactions</Heading>
        </CardHeader>
        <CardBody>
          <Table variant="simple" size="sm">
            <Thead>
              <Tr>
                <Th>Date</Th>
                <Th>Description</Th>
                <Th>Category</Th>
                <Th isNumeric>Amount</Th>
              </Tr>
            </Thead>
            <Tbody>
              {transactions.map((tx) => (
                <Tr key={tx.id}>
                  <Td>{tx.date}</Td>
                  <Td>{tx.merchant_name || tx.name}</Td>
                  <Td><Badge>{tx.category}</Badge></Td>
                  <Td isNumeric color={tx.amount < 0 ? 'red.500' : 'green.500'}>
                    ${Math.abs(tx.amount).toFixed(2)}
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </CardBody>
      </Card>
    </VStack>
  )
}

export default Finance
