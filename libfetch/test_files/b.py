import os

def create_pom_xml(directory="."):
    content = """\
<project>
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.example</groupId>
  <artifactId>sample-maven-project</artifactId>
  <version>1.0.0</version>
  <dependencies>
    <dependency>
      <groupId>org.apache.commons</groupId>
      <artifactId>commons-lang3</artifactId>
      <version>3.12.0</version>
    </dependency>
    <dependency>
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>4.13.2</version>
      <scope>test</scope>
    </dependency>
  </dependencies>
</project>
"""
    file_path = os.path.join(directory, "pom.xml")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created {file_path}")

if __name__ == "__main__":
    create_pom_xml()
