import os

def create_sample_files(base_dir="."):
    # 1. Python
    py_dir = os.path.join(base_dir, "python_example")
    os.makedirs(py_dir, exist_ok=True)
    with open(os.path.join(py_dir, "sample.py"), "w", encoding="utf-8") as f:
        f.write("""\
import os
import re
from math import sqrt
""")

    # 2. Node
    node_dir = os.path.join(base_dir, "node_example")
    os.makedirs(node_dir, exist_ok=True)
    package_json = {
        "name": "sample-node-project",
        "version": "1.0.0",
        "dependencies": {
            "express": "^4.17.1",
            "lodash": "^4.17.21"
        },
        "devDependencies": {
            "jest": "^26.6.3"
        }
    }
    import json
    with open(os.path.join(node_dir, "package.json"), "w", encoding="utf-8") as f:
        json.dump(package_json, f, indent=2)

    # 3. Ruby
    ruby_dir = os.path.join(base_dir, "ruby_example")
    os.makedirs(ruby_dir, exist_ok=True)
    with open(os.path.join(ruby_dir, "Gemfile"), "w", encoding="utf-8") as f:
        f.write("""\
source "https://rubygems.org"

gem "rails"
gem "nokogiri"
""")

    # 4. PHP
    php_dir = os.path.join(base_dir, "php_example")
    os.makedirs(php_dir, exist_ok=True)
    composer_json = {
        "require": {
            "monolog/monolog": "^2.0",
            "guzzlehttp/guzzle": "^7.0"
        },
        "require-dev": {
            "phpunit/phpunit": "^9.0"
        }
    }
    with open(os.path.join(php_dir, "composer.json"), "w", encoding="utf-8") as f:
        json.dump(composer_json, f, indent=2)

    # 5. Maven
    maven_dir = os.path.join(base_dir, "maven_example")
    os.makedirs(maven_dir, exist_ok=True)
    pom_xml = """\
<project xmlns="http://maven.apache.org/POM/4.0.0" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
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
    with open(os.path.join(maven_dir, "pom.xml"), "w", encoding="utf-8") as f:
        f.write(pom_xml)

    # 6. NuGet (.NET)
    nuget_dir = os.path.join(base_dir, "nuget_example")
    os.makedirs(nuget_dir, exist_ok=True)
    # Sample .csproj
    csproj_content = """\
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net6.0</TargetFramework>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Newtonsoft.Json" Version="13.0.1" />
    <PackageReference Include="Serilog" Version="2.10.0" />
  </ItemGroup>
</Project>
"""
    with open(os.path.join(nuget_dir, "sample.csproj"), "w", encoding="utf-8") as f:
        f.write(csproj_content)
    # packages.config
    packages_config_content = """\
<packages>
  <package id="NUnit" version="3.12.0" />
  <package id="Moq" version="4.15.2" />
</packages>
"""
    with open(os.path.join(nuget_dir, "packages.config"), "w", encoding="utf-8") as f:
        f.write(packages_config_content)

    # 7. Go
    go_dir = os.path.join(base_dir, "go_example")
    os.makedirs(go_dir, exist_ok=True)
    go_mod_content = """\
module example.com/goproject

go 1.17

require (
    github.com/gin-gonic/gin v1.7.7
    golang.org/x/mod v0.5.1
)
"""
    with open(os.path.join(go_dir, "go.mod"), "w", encoding="utf-8") as f:
        f.write(go_mod_content)

    # 8. Rust
    rust_dir = os.path.join(base_dir, "rust_example")
    os.makedirs(rust_dir, exist_ok=True)
    cargo_toml_content = """\
[package]
name = "rust_example"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = "1.0"
reqwest = "0.11"
"""
    with open(os.path.join(rust_dir, "Cargo.toml"), "w", encoding="utf-8") as f:
        f.write(cargo_toml_content)

    print(f"Sample files created under '{os.path.abspath(base_dir)}'")

if __name__ == "__main__":
    create_sample_files()
