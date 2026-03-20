import { useState, useEffect } from 'react'
import { Box, VStack, HStack, Text, Heading, Button, Card, CardBody, CardHeader, FormControl, FormLabel, Input, Select, Progress, SimpleGrid, Badge, Checkbox, CheckboxGroup, Wrap, WrapItem } from '@chakra-ui/react'
import { FiArrowLeft, FiArrowRight, FiCheck } from 'react-icons/fi'

const STEPS = [
  { key: 'welcome', title: 'Welcome', icon: '👋' },
  { key: 'profile', title: 'Profile', icon: '👤' },
  { key: 'goals', title: 'Goals', icon: '🎯' },
  { key: 'preferences', title: 'Preferences', icon: '⚙️' },
  { key: 'complete', title: 'Complete', icon: '🎉' }
]

const GOAL_OPTIONS = [
  { value: 'career_growth', label: 'Career Growth', icon: '📈' },
  { value: 'financial_independence', label: 'Financial Independence', icon: '💰' },
  { value: 'health_fitness', label: 'Health & Fitness', icon: '💪' },
  { value: 'relationships', label: 'Relationships', icon: '❤️' },
  { value: 'personal_development', label: 'Personal Development', icon: '🌱' },
  { value: 'business_building', label: 'Business Building', icon: '🏢' },
  { value: 'time_freedom', label: 'Time Freedom', icon: '⏰' }
]

function Onboarding() {
  const [step, setStep] = useState(0)
  const [formData, setFormData] = useState({
    display_name: '',
    role_title: '',
    company: '',
    location: '',
    bio: '',
    primary_goals: [],
    experience_level: 'beginner',
    timezone: 'UTC'
  })

  const progress = ((step + 1) / STEPS.length) * 100

  const handleNext = () => {
    if (step < STEPS.length - 1) {
      setStep(step + 1)
    }
  }

  const handleBack = () => {
    if (step > 0) {
      setStep(step - 1)
    }
  }

  const renderStep = () => {
    switch (STEPS[step].key) {
      case 'welcome':
        return (
          <VStack spacing={6} py={8}>
            <Text fontSize="6xl">👋</Text>
            <Heading size="lg">Welcome to Busy Bee!</Heading>
            <Text color="gray.500" textAlign="center" maxW="400px">
              Let's set up your personalized executive intelligence experience. 
              This will only take a few minutes.
            </Text>
            <SimpleGrid columns={2} spacing={4} w="full" maxW="400px">
              {STEPS.slice(0, -1).map((s) => (
                <HStack key={s.key} p={3} bg="gray.50" rounded="lg">
                  <Text fontSize="xl">{s.icon}</Text>
                  <Text fontSize="sm" fontWeight="500">{s.title}</Text>
                </HStack>
              ))}
            </SimpleGrid>
          </VStack>
        )

      case 'profile':
        return (
          <VStack spacing={4} align="stretch">
            <Heading size="md">Tell us about yourself</Heading>
            <Text color="gray.500" fontSize="sm">This helps us personalize your experience.</Text>
            
            <FormControl>
              <FormLabel fontSize="sm">Display Name *</FormLabel>
              <Input 
                value={formData.display_name}
                onChange={(e) => setFormData({...formData, display_name: e.target.value})}
                placeholder="How should we call you?"
              />
            </FormControl>
            
            <FormControl>
              <FormLabel fontSize="sm">Your Role/Title</FormLabel>
              <Input 
                value={formData.role_title}
                onChange={(e) => setFormData({...formData, role_title: e.target.value})}
                placeholder="e.g., Software Engineer, CEO, Student"
              />
            </FormControl>
            
            <FormControl>
              <FormLabel fontSize="sm">Company/Organization</FormLabel>
              <Input 
                value={formData.company}
                onChange={(e) => setFormData({...formData, company: e.target.value})}
                placeholder="e.g., Acme Inc"
              />
            </FormControl>
            
            <FormControl>
              <FormLabel fontSize="sm">Location</FormLabel>
              <Input 
                value={formData.location}
                onChange={(e) => setFormData({...formData, location: e.target.value})}
                placeholder="e.g., San Francisco, CA"
              />
            </FormControl>
          </VStack>
        )

      case 'goals':
        return (
          <VStack spacing={4} align="stretch">
            <Heading size="md">What do you want to achieve?</Heading>
            <Text color="gray.500" fontSize="sm">Select your primary goals. You can change these anytime.</Text>
            
            <FormControl>
              <FormLabel fontSize="sm">Primary Goals (select all that apply)</FormLabel>
              <CheckboxGroup value={formData.primary_goals} onChange={(vals) => setFormData({...formData, primary_goals: vals})}>
                <Wrap spacing={3}>
                  {GOAL_OPTIONS.map((goal) => (
                    <WrapItem key={goal.value}>
                      <Checkbox value={goal.value}>
                        <HStack>
                          <Text>{goal.icon}</Text>
                          <Text>{goal.label}</Text>
                        </HStack>
                      </Checkbox>
                    </WrapItem>
                  ))}
                </Wrap>
              </CheckboxGroup>
            </FormControl>
          </VStack>
        )

      case 'preferences':
        return (
          <VStack spacing={4} align="stretch">
            <Heading size="md">Customize your experience</Heading>
            <Text color="gray.500" fontSize="sm">Set your preferences for notifications and display.</Text>
            
            <FormControl>
              <FormLabel fontSize="sm">Experience Level</FormLabel>
              <Select 
                value={formData.experience_level}
                onChange={(e) => setFormData({...formData, experience_level: e.target.value})}
              >
                <option value="beginner">Beginner - Just getting started</option>
                <option value="intermediate">Intermediate - Some experience</option>
                <option value="advanced">Advanced - Experienced user</option>
                <option value="expert">Expert - Power user</option>
              </Select>
            </FormControl>
            
            <FormControl>
              <FormLabel fontSize="sm">Timezone</FormLabel>
              <Select 
                value={formData.timezone}
                onChange={(e) => setFormData({...formData, timezone: e.target.value})}
              >
                <option value="UTC">UTC</option>
                <option value="America/New_York">Eastern Time</option>
                <option value="America/Los_Angeles">Pacific Time</option>
                <option value="Europe/London">London</option>
              </Select>
            </FormControl>
          </VStack>
        )

      case 'complete':
        return (
          <VStack spacing={6} py={8}>
            <Text fontSize="6xl">🎉</Text>
            <Heading size="lg">You're all set!</Heading>
            <Text color="gray.500" textAlign="center" maxW="400px">
              Your Busy Bee account is ready. Start exploring your executive intelligence dashboard!
            </Text>
            <VStack spacing={2}>
              <HStack>
                <FiCheck color="green" />
                <Text>Profile created</Text>
              </HStack>
              <HStack>
                <FiCheck color="green" />
                <Text>Goals configured</Text>
              </HStack>
              <HStack>
                <FiCheck color="green" />
                <Text>Preferences saved</Text>
              </HStack>
            </VStack>
          </VStack>
        )

      default:
        return null
    }
  }

  return (
    <Box minH="100vh" bg="gray.50" p={8}>
      <Box maxW="600px" mx="auto">
        <VStack spacing={6}>
          {/* Progress */}
          <Box w="full">
            <HStack justify="space-between" mb={2}>
              <Text fontSize="sm" color="gray.500">Step {step + 1} of {STEPS.length}</Text>
              <Text fontSize="sm" color="gray.500">{Math.round(progress)}%</Text>
            </HStack>
            <Progress value={progress} colorScheme="brand" borderRadius="full" />
          </Box>

          {/* Steps Indicator */}
          <HStack spacing={2}>
            {STEPS.map((s, i) => (
              <Box
                key={s.key}
                w={8}
                h={8}
                rounded="full"
                bg={i === step ? 'brand.500' : i < step ? 'green.500' : 'gray.200'}
                display="flex"
                alignItems="center"
                justifyContent="center"
                color="white"
                fontSize="sm"
                fontWeight="bold"
              >
                {i < step ? <FiCheck /> : i + 1}
              </Box>
            ))}
          </HStack>

          {/* Form Card */}
          <Card w="full">
            <CardBody p={6}>
              {renderStep()}
            </CardBody>
          </Card>

          {/* Navigation */}
          {STEPS[step].key !== 'welcome' && STEPS[step].key !== 'complete' && (
            <HStack justify="space-between" w="full">
              <Button variant="ghost" leftIcon={<FiArrowLeft />} onClick={handleBack}>
                Back
              </Button>
              <Button colorScheme="brand" rightIcon={<FiArrowRight />} onClick={handleNext}>
                Continue
              </Button>
            </HStack>
          )}

          {STEPS[step].key === 'complete' && (
            <Button colorScheme="brand" size="lg" onClick={() => window.location.href = '/dashboard'}>
              Go to Dashboard
            </Button>
          )}
        </VStack>
      </Box>
    </Box>
  )
}

export default Onboarding
