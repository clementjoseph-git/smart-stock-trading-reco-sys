import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Toolbar,
  AppBar,
  Typography,
  CssBaseline,
  Box
} from "@mui/material";
import Sentiment from "./components/Sentiment";
import Forecast from "./components/Forecast";
import Fundamentals from "./components/Fundamentals";
import Portfolio from "./components/Portfolio";

const drawerWidth = 240;

function App() {
  return (
    <Router>
      <Box sx={{ display: "flex" }}>
        <CssBaseline />
        <AppBar position="fixed" sx={{ zIndex: 1201 }}>
          <Toolbar>
            <Typography variant="h6" noWrap>
              Smart Stock Trading Dashboard
            </Typography>
          </Toolbar>
        </AppBar>

        <Drawer
          variant="permanent"
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: "border-box" }
          }}
        >
          <Toolbar />
          <List>
            <ListItem disablePadding>
              <ListItemButton component={Link} to="/sentiment">
                <ListItemText primary="Sentiment Analysis" />
              </ListItemButton>
            </ListItem>
            <ListItem disablePadding>
              <ListItemButton component={Link} to="/forecast">
                <ListItemText primary="Forecast" />
              </ListItemButton>
            </ListItem>
            <ListItem disablePadding>
              <ListItemButton component={Link} to="/fundamentals">
                <ListItemText primary="Fundamentals" />
              </ListItemButton>
            </ListItem>
            <ListItem disablePadding>
              <ListItemButton component={Link} to="/portfolio">
                <ListItemText primary="Portfolio" />
              </ListItemButton>
            </ListItem>
          </List>
        </Drawer>

        <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
          <Toolbar />
          <Routes>
            <Route path="/sentiment" element={<Sentiment />} />
            <Route path="/forecast" element={<Forecast />} />
            <Route path="/fundamentals" element={<Fundamentals />} />
            <Route path="/portfolio" element={<Portfolio />} />
            {/* Default route */}
            <Route path="/" element={<Sentiment />} />
          </Routes>
        </Box>
      </Box>
    </Router>
  );
}

export default App;
