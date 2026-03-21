import { useState, useEffect } from 'react'
import { Box, VStack, HStack, Text, Heading, Card, CardBody, CardHeader, SimpleGrid, Badge, Button, List, ListItem, ListIcon, Divider, Icon } from '@chakra-ui/react'
import { FiCheck, FiX, FiZap, FiStar, FiShield } from 'react-icons/fi'
import { useAuth } from '../context/AuthContext'

const plans = [
  {
    id: 'free',
    name: 'Free',
    price: 0,
    period: 'forever',
    description: 'Perfect for getting started',
    features: [
      '3 Goals',
      '10 Tasks',
      'Basic Analytics',
      '1 Week History',
      'Community Support',
    ],
    notIncluded: [
      'AI Assistant',
      'Advanced Analytics',
      'File Storage',
      'Priority Support',
    ],
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 29,
    period: 'month',
    description: 'Best for personal growth',
    popular: true,
    features: [
      'Unlimited Goals',
      'Unlimited Tasks',
      'Advanced Analytics',
      'Full History',
      'AI Assistant',
      'File Storage (1GB)',
      'Email Support',
    ],
    notIncluded: [
      'Team Features',
      'API Access',
      'White-label',
    ],
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 199,
    period: 'month',
    description: 'For teams and organizations',
    features: [
      'Everything in Pro',
      'Team Management',
      'API Access',
      'White-label',
      'Custom Integrations',
      'Dedicated Support',
      'SLA Guarantee',
      'Unlimited Storage',
    ],
    notIncluded: [],
  },
]

function Subscription() {
  const { user } = useAuth()
  const [currentPlan, setCurrentPlan] = useState('free')

  useEffect(() => {
    if (user?.subscription_tier) {
      setCurrentPlan(user.subscription_tier)
    }
  }, [user])

  const currentPlanData = plans.find(p => p.id === currentPlan) || plans[0]

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between">
          <VStack align="start" spacing={1}>
            <Heading size="lg">Subscription</Heading>
            <Text color="gray.500">Manage your plan and billing</Text>
          </VStack>
          <Badge fontSize="md" px={4} py={2} colorScheme="brand" variant="subtle">
            Current: {currentPlanData.name}
          </Badge>
        </HStack>

        {/* Current Plan Card */}
        <Card bg="brand.50" border="1px" borderColor="brand.200">
          <CardBody>
            <HStack justify="space-between">
              <VStack align="start" spacing={1}>
                <HStack>
                  <Text fontWeight="bold" fontSize="lg">{currentPlanData.name} Plan</Text>
                  {currentPlan === 'pro' && <Badge colorScheme="brand">Active</Badge>}
                </HStack>
                <Text color="gray.600">
                  {currentPlanData.price === 0 ? 'Free forever' : `$${currentPlanData.price}/${currentPlanData.period}`}
                </Text>
              </VStack>
              {currentPlan !== 'enterprise' && (
                <Button colorScheme="brand">Upgrade Plan</Button>
              )}
            </HStack>
          </CardBody>
        </Card>

        {/* Usage */}
        <Card>
          <CardHeader><Heading size="sm">Current Usage</Heading></CardHeader>
          <CardBody pt={0}>
            <SimpleGrid columns={4} spacing={4}>
              <VStack>
                <Text fontSize="2xl" fontWeight="bold">12</Text>
                <Text fontSize="sm" color="gray.500">Goals</Text>
              </VStack>
              <VStack>
                <Text fontSize="2xl" fontWeight="bold">47</Text>
                <Text fontSize="sm" color="gray.500">Tasks</Text>
              </VStack>
              <VStack>
                <Text fontSize="2xl" fontWeight="bold">156</Text>
                <Text fontSize="sm" color="gray.500">API Calls</Text>
              </VStack>
              <VStack>
                <Text fontSize="2xl" fontWeight="bold">0.1GB</Text>
                <Text fontSize="sm" color="gray.500">Storage</Text>
              </VStack>
            </SimpleGrid>
          </CardBody>
        </Card>

        {/* Plans */}
        <Heading size="md">Available Plans</Heading>
        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
          {plans.map(plan => (
            <Card key={plan.id} border={plan.popular ? '2px' : '1px'} borderColor={plan.popular ? 'brand.500' : 'gray.200'}>
              <CardBody>
                <VStack align="stretch" spacing={4}>
                  <HStack justify="space-between">
                    <VStack align="start" spacing={0}>
                      <HStack>
                        <Heading size="sm">{plan.name}</Heading>
                        {plan.popular && <Badge colorScheme="brand">Popular</Badge>}
                      </HStack>
                      <Text color="gray.500" fontSize="sm">{plan.description}</Text>
                    </VStack>
                  </HStack>
                  
                  <HStack align="baseline">
                    <Text fontSize="4xl" fontWeight="bold">${plan.price}</Text>
                    <Text color="gray.500">/{plan.period}</Text>
                  </HStack>

                  <Button 
                    colorScheme={plan.id === currentPlan ? 'gray' : 'brand'} 
                    variant={plan.id === currentPlan ? 'outline' : 'solid'}
                    isDisabled={plan.id === currentPlan}
                  >
                    {plan.id === currentPlan ? 'Current Plan' : plan.price === 0 ? 'Downgrade' : 'Upgrade'}
                  </Button>

                  <Divider />

                  <List spacing={2}>
                    {plan.features.map((feature, i) => (
                      <ListItem key={i} fontSize="sm">
                        <ListIcon as={FiCheck} color="green.500" />
                        {feature}
                      </ListItem>
                    ))}
                    {plan.notIncluded?.map((feature, i) => (
                      <ListItem key={i} fontSize="sm" color="gray.400">
                        <ListIcon as={FiX} color="gray.400" />
                        {feature}
                      </ListItem>
                    ))}
                  </List>
                </VStack>
              </CardBody>
            </Card>
          ))}
        </SimpleGrid>

        {/* FAQ or Support */}
        <Card>
          <CardHeader><Heading size="sm">Billing & Support</Heading></CardHeader>
          <CardBody>
            <SimpleGrid columns={2} spacing={4}>
              <VStack align="start" p={4} bg="gray.50" borderRadius="md">
                <Icon as={FiShield} boxSize={6} color="brand.500" />
                <Text fontWeight="500">Secure Billing</Text>
                <Text fontSize="sm" color="gray.500">Powered by Stripe</Text>
              </VStack>
              <VStack align="start" p={4} bg="gray.50" borderRadius="md">
                <Icon as={FiStar} boxSize={6} color="brand.500" />
                <Text fontWeight="500">Need Help?</Text>
                <Text fontSize="sm" color="gray.500">Contact support@busybee.app</Text>
              </VStack>
            </SimpleGrid>
          </CardBody>
        </Card>
      </VStack>
    </Box>
  )
}

export default Subscription
