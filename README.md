# Question-Paper-OBE-Agent

Team 6 - Question Paper Setting and OBE Analysis System
# Question-Paper-OBE-Agent



An agent-based system for assisting in question-paper setting using reusable skills, tools, memory, an MCP-style connector, and an OpenCLA/OpenClaw runtime.



\---



\# Project Overview



The \*\*Question-Paper-OBE-Agent\*\* is designed as a modular agentic system for supporting the question-paper generation workflow.



The project progressively integrates the concepts implemented in \*\*Lab 1 to Lab 6\*\*.



\### Overall Architecture



```text

Faculty Request

&#x20;      |

&#x20;      v

Question Paper Coordinator

&#x20;      |

&#x20;      +-------------------+

&#x20;      |                   |

&#x20;      v                   v

&#x20;    Skills              Tools

&#x20;      |                   |

&#x20;      v                   v

Question Paper        Question Bank

&#x20;   Skill                 Tool

&#x20;      |

&#x20;      +---------> Memory

&#x20;      |

&#x20;      +---------> MCP-Style Connector

&#x20;      |

&#x20;      +---------> OpenCLA/OpenClaw Runtime

&#x20;                      |

&#x20;                      v

&#x20;                  Audit Log

