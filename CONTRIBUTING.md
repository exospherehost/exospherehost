# Contributing to ExosphereHost

Thank you for your interest in contributing to ExosphereHost! We're building the future of AI workflow infrastructure together, and every contribution makes a difference.

## 🌟 Ways to Contribute

There are many ways to contribute to ExosphereHost:

- **🐛 Bug Reports**: Help us identify and fix issues
- **💡 Feature Requests**: Suggest new features or improvements
- **📝 Documentation**: Improve our docs and guides
- **💻 Code Contributions**: Submit bug fixes and new features
- **🛰️ Satellites**: Create new satellites for the community
- **🧪 Testing**: Help test new features and releases
- **🎨 Design**: Improve UI/UX for our tools and documentation
- **📢 Community**: Help others in Discord, forums, or GitHub discussions

## 🚀 Getting Started

### Prerequisites

Before you start contributing, make sure you have:

- **Python 3.12+** installed
- **Node.js 18+** (for landing page contributions)
- **Docker** (for local development)
- **Git** for version control
- **UV** package manager (recommended for Python projects)

### Development Environment Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/exospherehost.git
   cd exospherehost
   ```

2. **Set up the development environment:**
   ```bash
   # API Server
   cd api-server
   uv sync
   cp .env.example .env  # Configure your environment
   
   # State Manager
   cd ../state-manager
   uv sync
   cp .env.example .env
   
   # Python SDK
   cd ../python-sdk
   uv sync
   
   # Landing Page
   cd ../landing-page
   npm install
   ```

3. **Start the development services:**
   ```bash
   # Using Docker Compose (recommended)
   docker-compose -f docker-compose.dev.yml up -d
   
   # Or start services individually
   cd api-server && uv run python run.py &
   cd state-manager && uv run python run.py &
   cd landing-page && npm run dev &
   ```

4. **Verify the setup:**
   - API Server: http://localhost:8000
   - State Manager: http://localhost:8001
   - Landing Page: http://localhost:3000
   - Documentation: http://localhost:8080 (after running `mkdocs serve` in docs/)

## 🐛 Reporting Bugs

### Before Reporting

1. **Search existing issues** to avoid duplicates
2. **Check the latest version** - the bug might already be fixed
3. **Test in a clean environment** to isolate the issue

### Bug Report Template

When reporting a bug, please include:

```markdown
**Bug Description**
A clear description of what the bug is.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.12.1]
- ExosphereHost version: [e.g., 0.1.0]
- Browser (if applicable): [e.g., Chrome 120.0]

**Additional Context**
- Error messages or logs
- Screenshots (if helpful)
- Related configuration
```

## 💡 Suggesting Features

We love feature suggestions! Here's how to propose them effectively:

### Feature Request Template

```markdown
**Feature Summary**
A brief description of the feature.

**Problem Statement**
What problem does this feature solve?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
What other approaches did you consider?

**Use Cases**
- Use case 1: ...
- Use case 2: ...

**Implementation Notes**
Any technical considerations or suggestions.
```

### Feature Development Process

1. **Discussion**: Start with a GitHub issue or Discord discussion
2. **Design**: Create a design document for complex features
3. **Approval**: Get maintainer approval before starting implementation
4. **Implementation**: Follow our coding standards and best practices
5. **Review**: Submit PR for code review
6. **Testing**: Ensure comprehensive test coverage
7. **Documentation**: Update relevant documentation

## 💻 Code Contributions

### Development Workflow

1. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

2. **Make your changes** following our coding standards

3. **Test your changes**:
   ```bash
   # Run tests for the component you modified
   cd api-server && uv run pytest
   cd python-sdk && uv run pytest
   cd landing-page && npm test
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new satellite for image processing"
   # or
   git commit -m "fix: resolve authentication timeout issue"
   ```

5. **Push and create a Pull Request**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Coding Standards

#### Python Code Style

- **Follow PEP 8** for Python code formatting
- **Use type hints** for all function parameters and return types
- **Write docstrings** for all public functions and classes
- **Use async/await** for all I/O operations
- **Handle exceptions** gracefully with proper error messages

**Example:**
```python
from typing import Optional
from pydantic import BaseModel

class SatelliteConfig(BaseModel):
    """Configuration for satellite execution."""
    
    name: str
    timeout: int = 300
    retries: int = 3

async def execute_satellite(
    config: SatelliteConfig,
    inputs: dict[str, str]
) -> Optional[dict[str, str]]:
    """
    Execute a satellite with the given configuration and inputs.
    
    Args:
        config: Satellite configuration
        inputs: Input data for the satellite
        
    Returns:
        Satellite execution results or None if failed
        
    Raises:
        SatelliteExecutionError: If execution fails after retries
    """
    try:
        # Implementation here
        pass
    except Exception as e:
        logger.error(f"Satellite execution failed: {e}")
        raise SatelliteExecutionError(f"Failed to execute {config.name}") from e
```

#### TypeScript/JavaScript Code Style

- **Use TypeScript** for all new JavaScript code
- **Follow Prettier** formatting (configured in the project)
- **Use ESLint** rules (configured in the project)
- **Write JSDoc** comments for complex functions
- **Use React hooks** properly with dependencies

**Example:**
```typescript
interface SatelliteProps {
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  onStatusChange?: (status: string) => void;
}

/**
 * Satellite status component with real-time updates
 */
export const SatelliteStatus: React.FC<SatelliteProps> = ({
  name,
  status,
  onStatusChange
}) => {
  const [currentStatus, setCurrentStatus] = useState(status);
  
  useEffect(() => {
    // WebSocket connection for real-time updates
    const ws = new WebSocket(`ws://localhost:8001/satellites/${name}`);
    
    ws.onmessage = (event) => {
      const newStatus = JSON.parse(event.data).status;
      setCurrentStatus(newStatus);
      onStatusChange?.(newStatus);
    };
    
    return () => ws.close();
  }, [name, onStatusChange]);
  
  return (
    <div className={`satellite-status status-${currentStatus}`}>
      {name}: {currentStatus}
    </div>
  );
};
```

### Testing Guidelines

#### Python Testing

```python
import pytest
from unittest.mock import AsyncMock, patch
from your_module import SatelliteExecutor

class TestSatelliteExecutor:
    @pytest.fixture
    async def executor(self):
        return SatelliteExecutor(config={"timeout": 30})
    
    @pytest.mark.asyncio
    async def test_successful_execution(self, executor):
        """Test successful satellite execution."""
        inputs = {"data": "test"}
        result = await executor.execute(inputs)
        
        assert result is not None
        assert "output" in result
    
    @pytest.mark.asyncio
    async def test_execution_timeout(self, executor):
        """Test satellite execution timeout handling."""
        with patch('asyncio.wait_for', side_effect=asyncio.TimeoutError):
            with pytest.raises(SatelliteTimeoutError):
                await executor.execute({"data": "test"})
```

#### TypeScript/React Testing

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SatelliteStatus } from './SatelliteStatus';

describe('SatelliteStatus', () => {
  test('renders satellite name and status', () => {
    render(<SatelliteStatus name="test-satellite" status="running" />);
    
    expect(screen.getByText(/test-satellite: running/)).toBeInTheDocument();
  });
  
  test('calls onStatusChange when status updates', async () => {
    const mockOnStatusChange = jest.fn();
    
    render(
      <SatelliteStatus 
        name="test-satellite" 
        status="running"
        onStatusChange={mockOnStatusChange}
      />
    );
    
    // Mock WebSocket message
    const mockWs = new WebSocket('ws://localhost:8001/satellites/test-satellite');
    mockWs.onmessage({ data: JSON.stringify({ status: 'completed' }) });
    
    await waitFor(() => {
      expect(mockOnStatusChange).toHaveBeenCalledWith('completed');
    });
  });
});
```

### Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/) for consistent commit messages:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(api-server): add webhook satellite support
fix(state-manager): resolve race condition in state updates
docs(getting-started): add Python SDK installation guide
test(python-sdk): add integration tests for node execution
```

## 🛰️ Creating Satellites

Satellites are the building blocks of ExosphereHost workflows. Here's how to create your own:

### Satellite Development Guidelines

1. **Follow the satellite interface**:
   ```python
   from exospherehost.satellite import BaseSatellite
   from pydantic import BaseModel
   
   class MySatellite(BaseSatellite):
       class Config(BaseModel):
           parameter1: str
           parameter2: int = 10
       
       class Input(BaseModel):
           data: str
       
       class Output(BaseModel):
           result: str
           metadata: dict[str, str]
       
       async def execute(
           self, 
           config: Config, 
           input_data: Input
       ) -> Output:
           # Your satellite logic here
           return Output(
               result="processed data",
               metadata={"processing_time": "1.2s"}
           )
   ```

2. **Make satellites idempotent**: Same input should always produce the same output

3. **Handle errors gracefully**: Return meaningful error messages

4. **Add comprehensive tests**: Test all edge cases and error conditions

5. **Document your satellite**: Include usage examples and parameter descriptions

### Satellite Submission Process

1. **Create the satellite** in the appropriate directory
2. **Add tests** and documentation
3. **Submit a Pull Request** with:
   - Clear description of the satellite's purpose
   - Usage examples
   - Test coverage report
   - Performance benchmarks (if applicable)

## 📝 Documentation Contributions

Good documentation is crucial for ExosphereHost's success. Here's how to contribute:

### Documentation Structure

```
docs/
├── docs/
│   ├── index.md              # Main documentation
│   ├── getting-started.md    # Getting started guide
│   ├── architecture.md       # Architecture overview
│   ├── api-server/          # API server docs
│   ├── satellites/          # Satellite documentation
│   └── python-sdk/          # SDK documentation
├── mkdocs.yml               # MkDocs configuration
└── README.md                # Documentation README
```

### Writing Guidelines

- **Use clear, concise language**
- **Include practical examples**
- **Add code snippets** with syntax highlighting
- **Use consistent formatting** with Markdown
- **Link to related documentation**
- **Test all code examples**

### Documentation Development

1. **Set up MkDocs**:
   ```bash
   cd docs
   uv sync
   uv run mkdocs serve
   ```

2. **Make your changes** to the relevant `.md` files

3. **Preview your changes** at http://localhost:8000

4. **Test all links and examples**

5. **Submit a Pull Request**

## 🧪 Testing Contributions

Help us maintain high code quality by contributing tests:

### Test Types

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Test system performance and scalability

### Running Tests

```bash
# Run all tests
./scripts/test-all.sh

# Run specific component tests
cd api-server && uv run pytest
cd python-sdk && uv run pytest -v
cd landing-page && npm test

# Run with coverage
cd api-server && uv run pytest --cov=app --cov-report=html
```

### Test Coverage Goals

- **Minimum coverage**: 80% for all components
- **Critical paths**: 95% coverage required
- **New features**: Must include comprehensive tests

## 🎨 Design Contributions

Help us improve the user experience:

### Design Areas

- **Landing Page UI/UX**: Improve the main website
- **Documentation Design**: Make docs more visually appealing
- **API Documentation**: Improve Swagger/OpenAPI presentation
- **Dashboard Mockups**: Design future dashboard interfaces
- **Brand Assets**: Create logos, icons, and graphics

### Design Process

1. **Discuss your ideas** in GitHub issues or Discord
2. **Create mockups** using Figma, Sketch, or similar tools
3. **Get feedback** from the community and maintainers
4. **Implement** the approved designs
5. **Test** across different devices and browsers

## 🤝 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before participating.

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests, technical discussions
- **GitHub Discussions**: General questions, ideas, and community chat
- **Discord**: Real-time chat, community support, and collaboration
- **Email**: Direct contact with maintainers for sensitive issues

### Community Best Practices

- **Be respectful** and constructive in all interactions
- **Help others** when you can
- **Share knowledge** and learning resources
- **Give credit** where credit is due
- **Welcome newcomers** and help them get started

## 🏆 Recognition

We believe in recognizing contributors:

### Contributor Recognition

- **Contributors Graph**: Automatic recognition on GitHub
- **Contributors Page**: Featured on our documentation site
- **Special Mentions**: In release notes and announcements
- **Swag**: T-shirts and stickers for significant contributors
- **Conference Opportunities**: Speaking opportunities at events

### Maintainer Path

Interested in becoming a maintainer? Here's the typical path:

1. **Regular Contributions**: Consistent, quality contributions over time
2. **Community Involvement**: Active participation in discussions and support
3. **Technical Expertise**: Deep understanding of the codebase
4. **Leadership**: Mentoring other contributors
5. **Invitation**: Current maintainers will invite qualified contributors

## 📋 Pull Request Process

### Before Submitting

- [ ] **Tests pass**: All existing tests continue to pass
- [ ] **New tests added**: For new features or bug fixes
- [ ] **Documentation updated**: For user-facing changes
- [ ] **Code formatted**: Following project style guidelines
- [ ] **Commits squashed**: Related commits combined into logical units

### PR Template

```markdown
## Description
Brief description of the changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings introduced
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and checks
2. **Maintainer Review**: At least one maintainer reviews the code
3. **Community Feedback**: Other contributors may provide feedback
4. **Revisions**: Address feedback and make necessary changes
5. **Approval**: Maintainer approves and merges the PR

## 🚀 Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **Major (X.0.0)**: Breaking changes
- **Minor (0.X.0)**: New features, backwards compatible
- **Patch (0.0.X)**: Bug fixes, backwards compatible

### Release Schedule

- **Patch releases**: As needed for critical bug fixes
- **Minor releases**: Monthly, with new features
- **Major releases**: Quarterly, with significant changes

## 📞 Getting Help

Need help contributing? Here's where to get support:

- **GitHub Discussions**: For general questions and help
- **Discord**: Real-time chat support
- **Documentation**: Comprehensive guides and examples
- **Email**: [nivedit@exosphere.host](mailto:nivedit@exosphere.host) for direct support

## 🎯 Current Priorities

Help us focus on what matters most:

### High Priority
- **🛰️ New Satellites**: Image processing, database operations, ML inference
- **📊 Monitoring**: Enhanced observability and metrics
- **🔒 Security**: Authentication improvements and security audits
- **📝 Documentation**: API documentation and tutorials

### Medium Priority
- **🎨 UI/UX**: Dashboard and visualization improvements
- **🧪 Testing**: Expanded test coverage and E2E tests
- **⚡ Performance**: Optimization and scalability improvements
- **🌐 Internationalization**: Multi-language support

### Future Considerations
- **📱 Mobile Support**: Mobile-friendly interfaces
- **🤖 AI Integration**: AI-powered workflow optimization
- **🔗 Integrations**: Third-party service integrations
- **📈 Analytics**: Advanced workflow analytics

---

**Thank you for contributing to ExosphereHost! Together, we're building the future of AI workflow infrastructure. 🚀**

For questions about contributing, reach out to us:
- **Discord**: [Join our community](https://discord.gg/JzCT6HRN)
- **Email**: [nivedit@exosphere.host](mailto:nivedit@exosphere.host)
- **GitHub**: [Create an issue](https://github.com/exospherehost/exospherehost/issues)