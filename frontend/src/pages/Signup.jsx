import { useState } from 'react'
import { Box, VStack, HStack, Text, Button, Input, FormControl, FormLabel, Link, Alert, AlertIcon, InputGroup, InputRightElement, IconButton } from '@chakra-ui/react'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import { FiEye, FiEyeOff } from 'react-icons/fi'
import { useAuth } from '../context/AuthContext'

function Signup() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const { signup, error } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    const result = await signup(email, password, fullName)
    setLoading(false)
    if (result) {
      setSuccess(true)
    }
  }

  if (success) {
    return (
      <Box minH="100vh" display="flex" alignItems="center" justifyContent="center" bg="gray.50" p={4}>
        <Box w="full" maxW="400px" bg="white" p={8} rounded="2xl" boxShadow="sm" textAlign="center">
          <VStack spacing={4}>
            <Text fontSize="4xl">✅</Text>
            <Text fontSize="xl" fontWeight="600">Check your email!</Text>
            <Text color="gray.500">We've sent a verification link to {email}</Text>
            <Link as={RouterLink} to="/login" color="brand.500" fontWeight="500">
              Back to login
            </Link>
          </VStack>
        </Box>
      </Box>
    )
  }

  return (
    <Box minH="100vh" display="flex" alignItems="center" justifyContent="center" bg="gray.50" p={4}>
      <Box w="full" maxW="400px">
        <VStack mb={8} spacing={2}>
          <HStack spacing={2}>
            <Box w={12} h={12} bg="brand.500" rounded="xl" display="flex" alignItems="center" justifyContent="center">
              <Text fontSize="2xl" fontWeight="bold" color="white">B</Text>
            </Box>
            <VStack align="start" spacing={0}>
              <Text fontWeight="bold" fontSize="2xl">Busy Bee</Text>
              <Text fontSize="sm" color="gray.500">Create your account</Text>
            </VStack>
          </HStack>
        </VStack>

        <Box bg="white" p={8} rounded="2xl" boxShadow="sm">
          <VStack spacing={6} as="form" onSubmit={handleSubmit}>
            {error && (
              <Alert status="error" borderRadius="lg">
                <AlertIcon />
                {error}
              </Alert>
            )}

            <FormControl>
              <FormLabel fontSize="sm">Full Name</FormLabel>
              <Input placeholder="John Doe" value={fullName} onChange={(e) => setFullName(e.target.value)} />
            </FormControl>

            <FormControl>
              <FormLabel fontSize="sm">Email</FormLabel>
              <Input type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </FormControl>

            <FormControl>
              <FormLabel fontSize="sm">Password</FormLabel>
              <InputGroup>
                <Input type={showPassword ? 'text' : 'password'} placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} required />
                <InputRightElement>
                  <IconButton variant="ghost" size="sm" icon={showPassword ? <FiEyeOff /> : <FiEye />} onClick={() => setShowPassword(!showPassword)} />
                </InputRightElement>
              </InputGroup>
            </FormControl>

            <Button type="submit" w="full" size="lg" isLoading={loading} loadingText="Creating account...">
              Create Account
            </Button>

            <HStack w="full" justify="center" spacing={1}>
              <Text fontSize="sm" color="gray.500">Already have an account?</Text>
              <Link as={RouterLink} to="/login" fontSize="sm" color="brand.500" fontWeight="500">Sign in</Link>
            </HStack>
          </VStack>
        </Box>
      </Box>
    </Box>
  )
}

export default Signup
