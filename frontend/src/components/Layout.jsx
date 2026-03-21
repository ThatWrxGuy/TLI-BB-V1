import { Box, Flex, HStack, VStack, Text, Avatar, Menu, MenuButton, MenuList, MenuItem, IconButton, useDisclosure, Drawer, DrawerOverlay, DrawerContent, DrawerBody, useBreakpointValue } from '@chakra-ui/react'
import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { FiHome, FiGrid, FiDollarSign, FiUser, FiSettings, FiLogOut, FiMenu, FiX, FiBell, FiActivity, FiBarChart2, FiTrendingUp, FiTarget, FiCheck, FiCreditCard, FiHelpCircle } from 'react-icons/fi'
import { useAuth } from '../context/AuthContext'

const NavItem = ({ to, icon: Icon, children, onClick }) => {
  const location = useLocation()
  const isActive = location.pathname === to

  return (
    <NavLink to={to} onClick={onClick}>
      <HStack
        px={4}
        py={2}
        rounded="lg"
        bg={isActive ? 'brand.50' : 'transparent'}
        color={isActive ? 'brand.600' : 'gray.600'}
        _hover={{ bg: 'brand.50', color: 'brand.600' }}
        transition="all 0.2s"
        spacing={3}
      >
        <Icon size={20} />
        <Text fontWeight={isActive ? '600' : '500'}>{children}</Text>
      </HStack>
    </NavLink>
  )
}

function Sidebar({ onClose }) {
  const { user, logout } = useAuth()

  return (
    <VStack h="full" py={6} spacing={6} align="stretch">
      {/* Logo */}
      <HStack px={4} spacing={3}>
        <Box
          w={10}
          h={10}
          bg="brand.500"
          rounded="lg"
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <Text fontSize="xl" fontWeight="bold" color="white">B</Text>
        </Box>
        <VStack align="start" spacing={0}>
          <Text fontWeight="bold" fontSize="lg">Busy Bee</Text>
          <Text fontSize="xs" color="gray.500">Executive Intelligence</Text>
        </VStack>
      </HStack>

      {/* Main Nav */}
      <VStack px={2} spacing={1} align="stretch" flex={1}>
        <Text fontSize="xs" fontWeight="600" color="gray.400" px={3} py={2}>MAIN</Text>
        <NavItem to="/dashboard" icon={FiHome} onClick={onClose}>Dashboard</NavItem>
        <NavItem to="/goals" icon={FiTarget} onClick={onClose}>Goals</NavItem>
        <NavItem to="/tasks" icon={FiCheck} onClick={onClose}>Tasks</NavItem>
        <NavItem to="/my-analytics" icon={FiTrendingUp} onClick={onClose}>My Analytics</NavItem>
        <NavItem to="/finance" icon={FiDollarSign} onClick={onClose}>Finance</NavItem>
      </VStack>

      {/* Support Section */}
      <VStack px={2} spacing={1} align="stretch">
        <Text fontSize="xs" fontWeight="600" color="gray.400" px={3} py={2}>SUPPORT</Text>
        <NavItem to="/notifications" icon={FiBell} onClick={onClose}>Notifications</NavItem>
        <NavItem to="/subscription" icon={FiCreditCard} onClick={onClose}>Subscription</NavItem>
        <NavItem to="/help" icon={FiHelpCircle} onClick={onClose}>Help & Support</NavItem>
      </VStack>

      {/* Account Section */}
      <VStack px={2} spacing={1} align="stretch">
        <Text fontSize="xs" fontWeight="600" color="gray.400" px={3} py={2}>ACCOUNT</Text>
        <NavItem to="/profile" icon={FiUser} onClick={onClose}>Profile</NavItem>
        <NavItem to="/settings" icon={FiSettings} onClick={onClose}>Settings</NavItem>
      </VStack>

      {/* User */}
      <Box px={4} pt={4} borderTop="1px" borderColor="gray.100">
        <Menu>
          <MenuButton w="full">
            <HStack spacing={3} p={2} rounded="lg" _hover={{ bg: 'gray.50' }}>
              <Avatar size="sm" name={user?.full_name || user?.email} />
              <VStack align="start" spacing={0} flex={1}>
                <Text fontSize="sm" fontWeight="500" noOfLines={1}>{user?.full_name || 'User'}</Text>
                <Text fontSize="xs" color="gray.500" noOfLines={1}>{user?.email}</Text>
              </VStack>
            </HStack>
          </MenuButton>
          <MenuList>
            <MenuItem icon={<FiUser />}>Profile</MenuItem>
            <MenuItem icon={<FiSettings />}>Settings</MenuItem>
            <MenuItem icon={<FiLogOut />} onClick={logout}>Logout</MenuItem>
          </MenuList>
        </Menu>
      </Box>
    </VStack>
  )
}

function Layout() {
  const { isOpen, onOpen, onClose } = useDisclosure()
  const isMobile = useBreakpointValue({ base: true, md: false })

  return (
    <Flex h="100vh">
      {/* Sidebar - Desktop */}
      {!isMobile && (
        <Box w="260px" bg="white" borderRight="1px" borderColor="gray.100">
          <Sidebar />
        </Box>
      )}

      {/* Mobile Drawer */}
      <Drawer isOpen={isOpen} placement="left" onClose={onClose}>
        <DrawerOverlay />
        <DrawerContent>
          <DrawerBody p={0}>
            <Sidebar onClose={onClose} />
          </DrawerBody>
        </DrawerContent>
      </Drawer>

      {/* Main Content */}
      <Box flex={1} overflow="auto">
        {/* Mobile Header */}
        {isMobile && (
          <Flex
            px={4}
            py={3}
            bg="white"
            borderBottom="1px"
            borderColor="gray.100"
            align="center"
            justify="space-between"
          >
            <IconButton icon={<FiMenu />} variant="ghost" onClick={onOpen} />
            <HStack spacing={2}>
              <IconButton icon={<FiBell />} variant="ghost" />
              <Box w={8} h={8} bg="brand.500" rounded="lg" display="flex" alignItems="center" justifyContent="center">
                <Text fontWeight="bold" color="white">B</Text>
              </Box>
            </HStack>
          </Flex>
        )}

        {/* Page Content */}
        <Box p={{ base: 4, md: 6 }}>
          <Outlet />
        </Box>
      </Box>
    </Flex>
  )
}

export default Layout
