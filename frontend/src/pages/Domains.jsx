import { useState, useEffect } from 'react'
import { Box, VStack, HStack, Text, Heading, Card, CardBody, CardHeader, SimpleGrid, Badge, Button, Progress, IconButton, Tabs, TabList, Tab, TabPanels, TabPanel, Input, InputGroup, InputLeftElement, Select, Stat, StatLabel, StatNumber, StatHelpText } from '@chakra-ui/react'
import { FiPlus, FiSearch, FiTrendingUp, FiTarget, FiCheck, FiZap, FiArrowRight, FiCalendar } from 'react-icons/fi'
import { domainsAPI } from '../services/api'

const domainIcons = {
  health: '🏃',
  career: '💼',
  mindset: '🧠',
  habits: '🔄',
  relationships: '👥',
  finance: '💰'
}

const domainColors = {
  health: 'green',
  career: 'blue',
  mindset: 'purple',
  habits: 'orange',
  relationships: 'pink',
  finance: 'yellow'
}

function DomainCard({ domain, progress, onClick }) {
  const color = domainColors[domain.id] || 'gray'
  
  return (
    <Card 
      cursor="pointer" 
      onClick={onClick}
      _hover={{ transform: 'translateY(-4px)', shadow: 'lg' }}
      transition="all 0.2s"
      borderTop="4px"
      borderTopColor={`${color}.400`}
    >
      <CardBody>
        <VStack align="stretch" spacing={3}>
          <HStack justify="space-between">
            <Text fontSize="3xl">{domain.icon}</Text>
            <Badge colorScheme={color} variant="subtle">{progress?.current_streak || 0} 🔥</Badge>
          </HStack>
          
          <VStack align="stretch" spacing={1}>
            <Heading size="sm">{domain.name}</Heading>
            <Text fontSize="xs" color="gray.500" noOfLines={2}>{domain.description}</Text>
          </VStack>
          
          <Box>
            <HStack justify="space-between" mb={1}>
              <Text fontSize="xs" color="gray.500">{progress?.active_goals || 0} active goals</Text>
              <Text fontSize="xs" fontWeight="bold" color={`${color}.500`}>{progress?.completion_rate || 0}%</Text>
            </HStack>
            <Progress value={progress?.completion_rate || 0} colorScheme={color} size="sm" borderRadius="full" />
          </Box>
        </VStack>
      </CardBody>
    </Card>
  )
}

function DomainDetail({ domain, onBack }) {
  const [goals, setGoals] = useState([])
  const [progress, setProgress] = useState(null)
  const [checkins, setCheckins] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDomainData()
  }, [domain.id])

  const loadDomainData = async () => {
    setLoading(true)
    try {
      const [goalsRes, progressRes, checkinsRes] = await Promise.all([
        domainsAPI.getDomainGoals(domain.id),
        domainsAPI.getDomainProgress(domain.id),
        domainsAPI.getDomainCheckins(domain.id, 7)
      ])
      setGoals(goalsRes.data)
      setProgress(progressRes.data)
      setCheckins(checkinsRes.data)
    } catch (err) {
      console.error('Failed to load domain:', err)
    } finally {
      setLoading(false)
    }
  }

  const color = domainColors[domain.id] || 'gray'

  return (
    <VStack spacing={6} align="stretch">
      {/* Header */}
      <HStack justify="space-between">
        <HStack>
          <Button variant="ghost" onClick={onBack}>← Back</Button>
          <Text fontSize="3xl">{domain.icon}</Text>
          <VStack align="start" spacing={0}>
            <Heading size="lg">{domain.name}</Heading>
            <Text fontSize="sm" color="gray.500">{domain.description}</Text>
          </VStack>
        </HStack>
        <Button leftIcon={<FiPlus />} colorScheme={color}>New Goal</Button>
      </HStack>

      {/* Stats */}
      <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
        <Card><CardBody textAlign="center"><Stat><StatLabel>Active Goals</StatLabel><StatNumber color={`${color}.500`}>{progress?.active_goals || 0}</StatNumber></Stat></CardBody></Card>
        <Card><CardBody textAlign="center"><Stat><StatLabel>Completed</StatLabel><StatNumber color="green.500">{progress?.completed_goals || 0}</StatNumber></Stat></CardBody></Card>
        <Card><CardBody textAlign="center"><Stat><StatLabel>Streak</StatLabel><StatNumber><HStack justify="center"><Text>{progress?.current_streak || 0}</Text><Text>🔥</Text></HStack></StatNumber></Stat></CardBody></Card>
        <Card><CardBody textAlign="center"><Stat><StatLabel>This Week</StatLabel><StatNumber>{progress?.weekly_checkins || 0}/7</StatNumber><StatHelpText>check-ins</StatHelpText></Stat></CardBody></Card>
      </SimpleGrid>

      {/* Check-ins Calendar */}
      <Card>
        <CardHeader><Heading size="sm">This Week's Check-ins</Heading></CardHeader>
        <CardBody>
          <HStack spacing={2} justify="space-around">
            {checkins.map((checkin, i) => (
              <VStack key={i} spacing={1}>
                <Text fontSize="xs" color="gray.500">{checkin.date.slice(5)}</Text>
                <Box w={10} h={10} borderRadius="full" bg={
                  checkin.status === 'completed' ? `${color}.100` :
                  checkin.status === 'partial' ? `${color}.50` : 'gray.100'
                } display="flex" alignItems="center" justifyContent="center">
                  {checkin.status === 'completed' ? '✓' : checkin.status === 'partial' ? '○' : '✗'}
                </Box>
              </VStack>
            ))}
          </HStack>
        </CardBody>
      </Card>

      {/* Goals */}
      <Card>
        <CardHeader>
          <HStack justify="space-between">
            <Heading size="sm">Goals</Heading>
            <Badge>{goals.length} total</Badge>
          </HStack>
        </CardHeader>
        <CardBody>
          {goals.length === 0 ? (
            <Text textAlign="center" color="gray.500">No goals yet. Create your first {domain.name} goal!</Text>
          ) : (
            <VStack spacing={3} align="stretch">
              {goals.map(goal => (
                <HStack key={goal.id} p={3} bg="gray.50" borderRadius="md" justify="space-between">
                  <VStack align="start" spacing={0} flex={1}>
                    <Text fontWeight="500">{goal.title}</Text>
                    <HStack>
                      <Badge size="sm" variant="subtle">{goal.category}</Badge>
                      <Text fontSize="xs" color="gray.500">{goal.progress}%</Text>
                    </HStack>
                  </VStack>
                  <Progress value={goal.progress} colorScheme={color} w="100px" size="sm" borderRadius="full" />
                </HStack>
              ))}
            </VStack>
          )}
        </CardBody>
      </Card>
    </VStack>
  )
}

export default function Domains() {
  const [domains, setDomains] = useState([])
  const [allProgress, setAllProgress] = useState({})
  const [loading, setLoading] = useState(true)
  const [selectedDomain, setSelectedDomain] = useState(null)

  useEffect(() => {
    loadDomains()
  }, [])

  const loadDomains = async () => {
    try {
      const [domainsRes, progressRes] = await Promise.all([
        domainsAPI.getDomains(),
        domainsAPI.getAllProgress()
      ])
      setDomains(domainsRes.data)
      setAllProgress(progressRes.data)
    } catch (err) {
      console.error('Failed to load domains:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <Box p={6}><Text>Loading...</Text></Box>
  }

  if (selectedDomain) {
    return (
      <Box p={6}>
        <DomainDetail 
          domain={selectedDomain} 
          onBack={() => setSelectedDomain(null)} 
        />
      </Box>
    )
  }

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between">
          <VStack align="start" spacing={1}>
            <Heading size="lg">Life Domains</Heading>
            <Text color="gray.500">Track all areas of your life</Text>
          </VStack>
        </HStack>

        {/* Domain Grid */}
        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
          {domains.map(domain => (
            <DomainCard 
              key={domain.id} 
              domain={domain} 
              progress={allProgress[domain.id]}
              onClick={() => setSelectedDomain(domain)}
            />
          ))}
        </SimpleGrid>

        {/* Weekly Overview */}
        <Card>
          <CardHeader>
            <Heading size="sm">Weekly Overview</Heading>
          </CardHeader>
          <CardBody>
            <SimpleGrid columns={6} spacing={2}>
              {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, i) => (
                <VStack key={day} spacing={1}>
                  <Text fontSize="xs" fontWeight="500">{day}</Text>
                  <Box w={8} h={8} borderRadius="md" bg={i < 4 ? 'green.100' : 'gray.100'} display="flex" alignItems="center" justifyContent="center">
                    {i < 4 ? '✓' : i < 6 ? '○' : ''}
                  </Box>
                </VStack>
              ))}
            </SimpleGrid>
          </CardBody>
        </Card>
      </VStack>
    </Box>
  )
}
