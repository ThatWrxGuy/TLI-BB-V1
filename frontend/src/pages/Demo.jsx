import { Box, VStack, Heading, Text, Button, Card, CardBody, CardHeader, SimpleGrid, Badge, HStack, Avatar, Divider } from '@chakra-ui/react'
import { FiCreditCard, FiCheck, FiShield, FiZap } from 'react-icons/fi'

function PricingCard({ tier, price, features, popular }) {
  return (
    <Card position="relative" border={popular ? '2px solid' : '1px'} borderColor={popular ? 'brand.500' : 'gray.200'}>
      {popular && (
        <Badge position="absolute" top={-3} right={4} colorScheme="brand">Most Popular</Badge>
      )}
      <CardHeader>
        <VStack align="start" spacing={1}>
          <Text fontWeight="bold" fontSize="xl">{tier}</Text>
          <HStack align="baseline">
            <Text fontSize="4xl" fontWeight="bold">{price}</Text>
            {price !== 'Free' && <Text color="gray.500">/month</Text>}
          </HStack>
        </VStack>
      </CardHeader>
      <CardBody pt={0}>
        <VStack align="stretch" spacing={3}>
          {features.map((feature, i) => (
            <HStack key={i} spacing={3}>
              <FiCheck color="#F59E0B" />
              <Text fontSize="sm">{feature}</Text>
            </HStack>
          ))}
          <Button mt={4} colorScheme={popular ? 'brand' : 'gray'} variant={popular ? 'solid' : 'outline'}>
            Get Started
          </Button>
        </VStack>
      </CardBody>
    </Card>
  )
}

function Demo() {
  return (
    <Box minH="100vh" bg="gray.50" p={8}>
      <VStack maxW="1200px" mx="auto" spacing={8}>
        <VStack spacing={4} textAlign="center">
          <Text fontSize="4xl">🐝</Text>
          <Heading size="xl">Try Busy Bee Free</Heading>
          <Text color="gray.600" maxW="600px">
            Experience the power of executive intelligence without commitment. 
            No credit card required.
          </Text>
        </VStack>

        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6} w="full">
          <PricingCard
            tier="Free"
            price="Free"
            features={[
              'Up to 3 goals',
              '10 tasks per month',
              '5 AI recommendations',
              'Basic dashboard',
              'Mood tracking',
              'Community support'
            ]}
          />
          <PricingCard
            tier="Pro"
            price="$29"
            popular
            features={[
              'Everything in Free',
              'Unlimited goals & tasks',
              'Unlimited AI recommendations',
              'Plaid finance integration',
              'Spending insights',
              'Priority support',
              'API access'
            ]}
          />
          <PricingCard
            tier="Enterprise"
            price="$99"
            features={[
              'Everything in Pro',
              'Admin panel',
              'Team management',
              'Custom integrations',
              'White-label options',
              'Dedicated support',
              'SLA guarantee'
            ]}
          />
        </SimpleGrid>

        <Text color="gray.500" fontSize="sm">
          All plans include 14-day free trial. Cancel anytime.
        </Text>
      </VStack>
    </Box>
  )
}

export default Demo
