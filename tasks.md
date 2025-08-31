# Real Work Challenge for the SaaS Chief Architect Position

## Assignment 2: SaaS Infrastructure Automation & Deployment Pipeline

### Scenario:

Our company is modernizing the infrastructure for an acquired SaaS product.

**Current state:**
- The product runs on AWS EC2 instances with **manual provisioning** via the AWS console.
- Deployments are **manually triggered** by running scripts on a jump box.
- There is **no infrastructure version control**, no automated testing in deployments, and no staging environment parity with production.
- Secrets are stored in plain text in application config files.

**Goal:**
- Implement a **secure, automated, and repeatable** infrastructure and deployment process using IaC and CI/CD best practices.

**Constraints:**
- **Cloud platform:** AWS or Azure
- **IaC tools allowed:** Terraform, AWS CloudFormation
- **CI/CD tools allowed:** GitHub Actions, GitLab CI, or Jenkins
- **Time:** The deliverable should be achievable in 4-6 hours by an experienced candidate (you can submit partial implementations if needed).
- **Security:** Must integrate secure secrets management.

### Your Task:

**Infrastructure as Code**
- Write IaC to provision the following in AWS:
  - VPC with public & private subnets
  - Two EC2 instances (one for staging, one for production) behind a load balancer
  - Security groups with least privilege access
  - S3 bucket for static assets
  - Infrastructure should be modular, parameterized, and reusable.

**CI/CD Pipeline**
- Create a pipeline that:
  - Runs automated tests on code push
  - Builds the application
  - Deploys to staging automatically on merge to develop branch
  - Deploys to production on an approved release from main branch
  - Stores build artifacts in S3 or ECR (depending on app type)
  - Include rollback capabilities.

**Secrets Management**
- Integrate with AWS Secrets Manager or SSM Parameter Store.
- Ensure secrets are never stored in plain text in repos or configs.

**Documentation**
- Provide a README.md describing:
  - How to deploy infrastructure
  - How the pipeline works
  - How rollback is performed
  - Security considerations

### Assignment Output:

**GitHub repo with:**
- IaC code (/infrastructure)
- CI/CD pipeline config (.github/workflows, .gitlab-ci.yml, or Jenkinsfile)
- Example application or placeholder code to deploy
- README.md with setup/run instructions

**Diagram** showing the deployed architecture & pipeline flow (Lucidchart/Miro/Draw.io acceptable)
- You can add the above diagram to the last slide of the presentation in the first assignment, mentioning in the title of the slide that the diagram is part of the second assignment.

**Estimated time to complete:** 3 days

### How to deliver the assignment:

- Once your deliverables are ready, copy-paste the link of the **GitHub repo** into the box below, and hit **Next Page**.