import { useState } from 'react'
import { Box, VStack, HStack, Text, Heading, Card, CardBody, CardHeader, Accordion, AccordionItem, AccordionButton, AccordionPanel, AccordionIcon, Input, InputGroup, InputLeftElement, Button, SimpleGrid, Icon, List, ListItem, ListIcon } from '@chakra-ui/react'
import { FiSearch, FiMail, FiMessageCircle, FiBook, FiVideo, FiExternalLink, FiCheck } from 'react-icons/fi'

const faqs = [
  {
    question: 'How do I create a goal?',
    answer: 'Click the "New Goal" button on the Goals page. Enter a title, description, and optional target date. You can also categorize your goal for better organization.'
  },
  {
    question: 'How does the streak system work?',
    answer: 'Your streak increases for each day you complete at least one task. If you miss a day, your streak resets. Maintain streaks to earn achievement badges!'
  },
  {
    question: 'How do I connect my bank account?',
    answer: 'Go to the Finance page and click "Link Account". We use Plaid to securely connect your bank. Your credentials are never stored on our servers.'
  },
  {
    question: 'Can I upgrade or downgrade my plan?',
    answer: 'Yes! Go to Subscription page to view and change your plan. Upgrades take effect immediately, while downgrades apply at the end of your billing cycle.'
  },
  {
    question: 'How do I enable two-factor authentication?',
    answer: 'Go to Settings > Security and enable Two-Factor Authentication. You can use an authenticator app or SMS verification.'
  },
  {
    question: 'Is my data secure?',
    answer: 'Yes! We use industry-standard encryption for all data. We never sell your personal information. See our Privacy Policy for details.'
  },
]

function Help() {
  const [search, setSearch] = useState('')

  const filteredFaqs = faqs.filter(faq => 
    faq.question.toLowerCase().includes(search.toLowerCase()) ||
    faq.answer.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <VStack align="start" spacing={1}>
          <Heading size="lg">Help & Support</Heading>
          <Text color="gray.500">Find answers or get in touch</Text>
        </VStack>

        {/* Search */}
        <InputGroup maxW="500px">
          <InputLeftElement><FiSearch /></InputLeftElement>
          <Input 
            placeholder="Search help articles..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </InputGroup>

        {/* Quick Links */}
        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
          <Card cursor="pointer" _hover={{ shadow: 'md' }}>
            <CardBody>
              <HStack spacing={4}>
                <Box p={3} bg="brand.50" borderRadius="lg">
                  <Icon as={FiBook} boxSize={6} color="brand.500" />
                </Box>
                <VStack align="start" spacing={0}>
                  <Text fontWeight="500">Knowledge Base</Text>
                  <Text fontSize="sm" color="gray.500">Browse articles</Text>
                </VStack>
              </HStack>
            </CardBody>
          </Card>

          <Card cursor="pointer" _hover={{ shadow: 'md' }}>
            <CardBody>
              <HStack spacing={4}>
                <Box p={3} bg="blue.50" borderRadius="lg">
                  <Icon as={FiMail} boxSize={6} color="blue.500" />
                </Box>
                <VStack align="start" spacing={0}>
                  <Text fontWeight="500">Email Support</Text>
                  <Text fontSize="sm" color="gray.500">support@busybee.app</Text>
                </VStack>
              </HStack>
            </CardBody>
          </Card>

          <Card cursor="pointer" _hover={{ shadow: 'md' }}>
            <CardBody>
              <HStack spacing={4}>
                <Box p={3} bg="green.50" borderRadius="lg">
                  <Icon as={FiMessageCircle} boxSize={6} color="green.500" />
                </Box>
                <VStack align="start" spacing={0}>
                  <Text fontWeight="500">Live Chat</Text>
                  <Text fontSize="sm" color="gray.500">Available 9-5 EST</Text>
                </VStack>
              </HStack>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* FAQs */}
        <Card>
          <CardHeader>
            <Heading size="sm">Frequently Asked Questions</Heading>
          </CardHeader>
          <CardBody pt={0}>
            <Accordion allowMultiple>
              {filteredFaqs.map((faq, index) => (
                <AccordionItem key={index} border="none">
                  <AccordionButton py={4}>
                    <Box flex="1" textAlign="left" fontWeight="500">
                      {faq.question}
                    </Box>
                    <AccordionIcon />
                  </AccordionButton>
                  <AccordionPanel pb={4}>
                    <Text color="gray.600">{faq.answer}</Text>
                  </AccordionPanel>
                </AccordionItem>
              ))}
            </Accordion>
          </CardBody>
        </Card>

        {/* Contact */}
        <Card>
          <CardHeader>
            <Heading size="sm">Still Need Help?</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4}>
              <Text color="gray.500">Can't find what you're looking for? We're here to help!</Text>
              <HStack>
                <Button leftIcon={<FiMail />} colorScheme="brand">Email Support</Button>
                <Button leftIcon={<FiMessageCircle />} variant="outline">Live Chat</Button>
              </HStack>
            </VStack>
          </CardBody>
        </Card>
      </VStack>
    </Box>
  )
}

export default Help
