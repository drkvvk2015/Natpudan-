import React, { useState, useEffect, useRef } from "react";
import {
  Container,
  Paper,
  Box,
  TextField,
  Typography,
  Button,
  CircularProgress,
  Card,
  CardContent,
  Grid,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import { Search, ZoomIn, ZoomOut, Download } from "@mui/icons-material";
import axios from "axios";

interface GraphNode {
  id: string;
  label: string;
  type: string; // disease, symptom, medication, procedure
  size: number;
  color: string;
}

interface GraphLink {
  source: string;
  target: string;
  weight: number;
}

interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

interface SearchResult {
  nodes: GraphNode[];
  links: GraphLink[];
  query: string;
}

interface NodeInfo {
  id: string;
  label: string;
  type: string;
  related_nodes: Array<{ label: string; type: string; relationship: string }>;
  description?: string;
}

const KnowledgeGraphVisualizer: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState<NodeInfo | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [zoom, setZoom] = useState(1);
  const svgRef = useRef<SVGSVGElement | null>(null);

  const typeColors: Record<string, string> = {
    disease: "#FF6B6B",
    symptom: "#FFE66D",
    medication: "#4ECDC4",
    procedure: "#95E1D3",
    condition: "#FF6B6B",
  };

  const searchGraph = async (query: string) => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await axios.get("/api/medical/knowledge/graph/search", {
        params: { concept: query },
      });
      setGraphData(response.data);
    } catch (err: any) {
      console.error("Search failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    searchGraph(searchQuery);
  };

  const handleNodeClick = async (nodeId: string) => {
    try {
      const response = await axios.get(
        `/api/medical/knowledge/graph/node/${nodeId}`
      );
      setSelectedNode(response.data);
      setDialogOpen(true);
    } catch (err: any) {
      console.error("Failed to load node details:", err);
    }
  };

  const downloadGraph = () => {
    if (!svgRef.current) return;

    const svg = svgRef.current.cloneNode(true) as SVGSVGElement;
    const serializer = new XMLSerializer();
    const svgString = serializer.serializeToString(svg);
    const blob = new Blob([svgString], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "knowledge-graph.svg";
    link.click();
  };

  useEffect(() => {
    // Load initial graph data
    const loadInitialData = async () => {
      try {
        setLoading(true);
        const response = await axios.get(
          "/api/medical/knowledge/graph/export/d3"
        );
        setGraphData(response.data);
      } catch (err: any) {
        console.error("Failed to load initial data:", err);
      } finally {
        setLoading(false);
      }
    };

    loadInitialData();
  }, []);

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: "bold" }}>
        Knowledge Graph Visualization
      </Typography>

      <Grid container spacing={3}>
        {/* Controls */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: "flex", gap: 2, alignItems: "center", flexWrap: "wrap" }}>
              <TextField
                placeholder="Search concept (e.g., diabetes, pneumonia)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSearch()}
                sx={{ flex: 1, minWidth: 250 }}
                variant="outlined"
              />
              <Button
                variant="contained"
                startIcon={<Search />}
                onClick={handleSearch}
                disabled={loading}
              >
                Search
              </Button>
              <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={downloadGraph}
                disabled={!graphData}
              >
                Export
              </Button>
              <Box sx={{ display: "flex", gap: 1 }}>
                <Button
                  size="small"
                  startIcon={<ZoomIn />}
                  onClick={() => setZoom(z => Math.min(z + 0.2, 3))}
                >
                  Zoom In
                </Button>
                <Button
                  size="small"
                  startIcon={<ZoomOut />}
                  onClick={() => setZoom(z => Math.max(z - 0.2, 0.5))}
                >
                  Zoom Out
                </Button>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Graph Visualization */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, minHeight: 600, position: "relative" }}>
            {loading ? (
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  height: 600,
                }}
              >
                <CircularProgress />
              </Box>
            ) : graphData ? (
              <svg
                ref={svgRef}
                style={{
                  width: "100%",
                  height: 600,
                  border: "1px solid #e0e0e0",
                  transform: `scale(${zoom})`,
                  transformOrigin: "top left",
                }}
              >
                {/* Draw links */}
                {graphData.links.map((link, i) => {
                  const sourceNode = graphData.nodes.find(n => n.id === link.source);
                  const targetNode = graphData.nodes.find(n => n.id === link.target);
                  if (!sourceNode || !targetNode) return null;

                  // Simple grid layout for demo
                  const sourceX = (i % 10) * 100 + 50;
                  const sourceY = Math.floor(i / 10) * 100 + 50;
                  const targetX = ((i + 1) % 10) * 100 + 50;
                  const targetY = Math.floor((i + 1) / 10) * 100 + 50;

                  return (
                    <line
                      key={`link-${i}`}
                      x1={sourceX}
                      y1={sourceY}
                      x2={targetX}
                      y2={targetY}
                      stroke="#999"
                      strokeOpacity={0.6}
                      strokeWidth={link.weight || 1}
                    />
                  );
                })}

                {/* Draw nodes */}
                {graphData.nodes.slice(0, 50).map((node, i) => {
                  const x = (i % 10) * 100 + 50;
                  const y = Math.floor(i / 10) * 100 + 50;
                  const nodeColor = typeColors[node.type] || "#999";
                  const nodeSize = Math.max(20, node.size || 30);

                  return (
                    <g
                      key={node.id}
                      onClick={() => handleNodeClick(node.id)}
                      style={{ cursor: "pointer" }}
                    >
                      <circle
                        cx={x}
                        cy={y}
                        r={nodeSize}
                        fill={nodeColor}
                        stroke="#333"
                        strokeWidth={2}
                        opacity={0.8}
                      />
                      <text
                        x={x}
                        y={y}
                        textAnchor="middle"
                        dy="0.3em"
                        fontSize={12}
                        fontWeight="bold"
                        pointerEvents="none"
                        fill="#333"
                      >
                        {node.label.substring(0, 8)}
                      </text>
                    </g>
                  );
                })}
              </svg>
            ) : (
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  height: 600,
                  color: "text.secondary",
                }}
              >
                Search for a concept to visualize the knowledge graph
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Legend */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Legend
            </Typography>
            <Box sx={{ display: "flex", flexWrap: "wrap", gap: 3 }}>
              {Object.entries(typeColors).map(([type, color]) => (
                <Box key={type} sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <Box
                    sx={{
                      width: 20,
                      height: 20,
                      borderRadius: "50%",
                      backgroundColor: color,
                      border: "1px solid #333",
                    }}
                  />
                  <Typography variant="body2" sx={{ textTransform: "capitalize" }}>
                    {type}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>

        {/* Statistics */}
        {graphData && (
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Graph Statistics
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6} sm={3}>
                  <Card>
                    <CardContent>
                      <Typography color="textSecondary" gutterBottom>
                        Total Nodes
                      </Typography>
                      <Typography variant="h6">
                        {graphData.nodes.length}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Card>
                    <CardContent>
                      <Typography color="textSecondary" gutterBottom>
                        Total Links
                      </Typography>
                      <Typography variant="h6">
                        {graphData.links.length}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Card>
                    <CardContent>
                      <Typography color="textSecondary" gutterBottom>
                        Diseases
                      </Typography>
                      <Typography variant="h6">
                        {graphData.nodes.filter(n => n.type === "disease").length}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Card>
                    <CardContent>
                      <Typography color="textSecondary" gutterBottom>
                        Medications
                      </Typography>
                      <Typography variant="h6">
                        {graphData.nodes.filter(n => n.type === "medication").length}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Paper>
          </Grid>
        )}
      </Grid>

      {/* Node Details Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Node Details</DialogTitle>
        <DialogContent>
          {selectedNode && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: "bold", mb: 1 }}>
                {selectedNode.label}
              </Typography>
              <Chip
                label={selectedNode.type}
                sx={{
                  backgroundColor: typeColors[selectedNode.type] || "#999",
                  color: "#fff",
                  mb: 2,
                }}
              />
              {selectedNode.description && (
                <Typography variant="body2" paragraph>
                  {selectedNode.description}
                </Typography>
              )}

              {selectedNode.related_nodes.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: "bold", mb: 1 }}>
                    Related Nodes
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Node</TableCell>
                          <TableCell>Type</TableCell>
                          <TableCell>Relationship</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {selectedNode.related_nodes.map((rel, i) => (
                          <TableRow key={i}>
                            <TableCell>{rel.label}</TableCell>
                            <TableCell>{rel.type}</TableCell>
                            <TableCell>{rel.relationship}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
      </Dialog>
    </Container>
  );
};

export default KnowledgeGraphVisualizer;
