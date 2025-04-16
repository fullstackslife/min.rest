import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Paper, 
  List, 
  ListItem, 
  ListItemText,
  Button,
  TextField,
  CircularProgress
} from '@mui/material';
import axios from 'axios';

interface Repository {
  name: string;
  path: string;
  type: 'file' | 'directory';
}

const App: React.FC = () => {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [command, setCommand] = useState('');
  const [output, setOutput] = useState('');

  useEffect(() => {
    fetchRepositories();
  }, []);

  const fetchRepositories = async () => {
    try {
      const response = await axios.get('/api/repositories');
      setRepositories(response.data);
    } catch (error) {
      console.error('Error fetching repositories:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCommandSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/execute', { command });
      setOutput(response.data.output);
      setCommand('');
    } catch (error) {
      console.error('Error executing command:', error);
      setOutput('Error executing command');
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Workspace Control Center
        </Typography>
        
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="h6" gutterBottom>
            Repositories
          </Typography>
          {loading ? (
            <CircularProgress />
          ) : (
            <List>
              {repositories.map((repo) => (
                <ListItem key={repo.path}>
                  <ListItemText
                    primary={repo.name}
                    secondary={repo.path}
                  />
                </ListItem>
              ))}
            </List>
          )}
        </Paper>

        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Command Interface
          </Typography>
          <form onSubmit={handleCommandSubmit}>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <TextField
                fullWidth
                variant="outlined"
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                placeholder="Enter command..."
              />
              <Button
                type="submit"
                variant="contained"
                color="primary"
              >
                Execute
              </Button>
            </Box>
          </form>
          {output && (
            <Paper sx={{ p: 2, bgcolor: 'grey.100' }}>
              <Typography variant="body1" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                {output}
              </Typography>
            </Paper>
          )}
        </Paper>
      </Box>
    </Container>
  );
};

export default App; 