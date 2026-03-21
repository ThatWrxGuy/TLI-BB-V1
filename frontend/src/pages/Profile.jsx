import { useState, useEffect } from 'react'
import { Box, VStack, HStack, Text, Heading, Avatar, Button, Card, CardBody, CardHeader, FormControl, FormLabel, Input, Badge, SimpleGrid, Divider } from '@chakra-ui/react'
import { useAuth } from '../context/AuthContext'
import { profileAPI } from '../services/api'

function Profile() {
  const { user } = useAuth()
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    try {
      const response = await profileAPI.getProfile()
      setProfile(response.data)
    } catch (err) {
      console.error('Failed to load profile:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <VStack spacing={6} align="stretch">
      <Heading size="lg">Profile</Heading>

      <Card>
        <CardBody>
          <HStack spacing={6}>
            <Avatar size="xl" name={user?.full_name || user?.email} />
            <VStack align="start" spacing={1}>
              <HStack>
                <Text fontSize="xl" fontWeight="bold">{profile?.full_name || 'User'}</Text>
                <Badge colorScheme="brand">{user?.subscription_tier || 'free'}</Badge>
              </HStack>
              <Text color="gray.500">{profile?.email || user?.email}</Text>
              <Text fontSize="sm" color="gray.400">Member since {new Date().toLocaleDateString()}</Text>
            </VStack>
          </HStack>
        </CardBody>
      </Card>

      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
        <Card>
          <CardHeader>
            <Heading size="sm">Account Info</Heading>
          </CardHeader>
          <CardBody pt={0}>
            <VStack align="stretch" spacing={4}>
              <FormControl>
                <FormLabel fontSize="sm">Full Name</FormLabel>
                <Input defaultValue={profile?.full_name || ''} />
              </FormControl>
              <FormControl>
                <FormLabel fontSize="sm">Display Name</FormLabel>
                <Input defaultValue={profile?.display_name || ''} />
              </FormControl>
              <Button colorScheme="brand" alignSelf="start">Save Changes</Button>
            </VStack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="sm">Stats</Heading>
          </CardHeader>
          <CardBody pt={0}>
            <SimpleGrid columns={2} spacing={4}>
              <Box>
                <Text fontSize="2xl" fontWeight="bold">12</Text>
                <Text fontSize="sm" color="gray.500">Goals Completed</Text>
              </Box>
              <Box>
                <Text fontSize="2xl" fontWeight="bold">48</Text>
                <Text fontSize="sm" color="gray.500">Tasks Done</Text>
              </Box>
              <Box>
                <Text fontSize="2xl" fontWeight="bold">23</Text>
                <Text fontSize="sm" color="gray.500">Day Streak</Text>
              </Box>
              <Box>
                <Text fontSize="2xl" fontWeight="bold">15</Text>
                <Text fontSize="sm" color="gray.500">AI Insights</Text>
              </Box>
            </SimpleGrid>
          </CardBody>
        </Card>
      </SimpleGrid>
    </VStack>
  )
}

export default Profile
