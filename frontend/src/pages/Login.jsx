import { useState } from 'react'
import { Box, VStack, HStack, Text, Button, Input, FormControl, FormLabel, Link, Alert, AlertIcon, InputGroup, InputRightElement, IconButton } from '@chakra-ui/react'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import { FiEye, FiEyeOff, FiMail, FiLock } from 'react-icons/fi'
import { useAuth } from '../context/AuthContext'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const { login, error } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    const success = await login(email, password)
    setLoading(false)
    if (success) {
      navigate('/dashboard')
    }
  }

  return (
    <Box minH="100vh" display="flex" alignItems="center" justifyContent="center" bg="gray.50" p={4}>
      <Box w="full" maxW="400px">
        {/* Logo */}
        <VStack mb={8} spacing={2}>
          <HStack spacing={2}>
            <Box
              w={12}
              h={12}
              bg="brand.500"
              rounded="xl"
              display="flex"
              alignItems="center"
              justifyContent="center"
            >
              <Text fontSize="2xl" fontWeight="bold" color="white">B</Text>
            </Box>
            <VStack align="start" spacing={0}>
              <Text fontWeight="bold" fontSize="2xl">Busy Bee</Text>
              <Text fontSize="sm" color="gray.500">Executive Intelligence</Text>
            </VStack>
          </HStack>
        </VStack>

        {/* Form */}
        <Box bg="white" p={8} rounded="2xl" boxShadow="sm">
          <VStack spacing={6} as="form" onSubmit={handleSubmit}>
            <Text fontSize="xl" fontWeight="600">Welcome back</Text>

            {error && (
              <Alert status="error" borderRadius="lg">
                <AlertIcon />
                {error}
              </Alert>
            )}

            <FormControl>
              <FormLabel fontSize="sm">Email</FormLabel>
              <InputGroup>
                <Input
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </InputGroup>
            </FormControl>

            <FormControl>
              <FormLabel fontSize="sm">Password</FormLabel>
              <InputGroup>
                <Input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <InputRightElement>
                  <IconButton
                    variant="ghost"
                    size="sm"
                    icon={showPassword ? <FiEyeOff /> : <FiEye />}
                    onClick={() => setShowPassword(!showPassword)}
                  />
                </InputRightElement>
              </InputGroup>
            </FormControl>

            <HStack w="full" justify="end">
              <Link as={RouterLink} to="/forgot-password" fontSize="sm" color="brand.500">
                Forgot password?
              </Link>
            </HStack>

            <Button
              type="submit"
              w="full"
              size="lg"
              isLoading={loading}
              loadingText="Signing in..."
            >
              Sign In
            </Button>

            <HStack w="full" justify="center" spacing={1}>
              <Text fontSize="sm" color="gray.500">Don't have an account?</Text>
              <Link as={RouterLink} to="/signup" fontSize="sm" color="brand.500" fontWeight="500">
                Sign up
              </Link>
            </HStack>

            <HStack w="full">
              <Box flex={1} h="1px" bg="gray.200" />
              <Text fontSize="sm" color="gray.400">or</Text>
              <Box flex={1} h="1px" bg="gray.200" />
            </HStack>

            <Button
              as={RouterLink}
              to="/demo"
              w="full"
              variant="outline"
            >
              Try Demo Mode
            </Button>
          </VStack>
        </Box>
      </Box>
    </Box>
  )
}

export default Login
