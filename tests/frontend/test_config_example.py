#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端组件测试配置 - Vue Test Utils 和 Jest 配置
Frontend Component Tests - Vue Test Utils and Jest Configuration

Author: chenlei
"""

# package.json 测试依赖配置示例
PACKAGE_JSON_TEST_DEPS = {
    "devDependencies": {
        "@vue/test-utils": "^2.4.0",
        "jest": "^29.0.0",
        "@vue/vue3-jest": "^29.0.0",
        "babel-jest": "^29.0.0",
        "jest-environment-jsdom": "^29.0.0",
        "@testing-library/vue": "^7.0.0",
        "@testing-library/jest-dom": "^5.16.0"
    },
    "scripts": {
        "test": "jest",
        "test:watch": "jest --watch",
        "test:coverage": "jest --coverage"
    }
}

# Jest 配置文件内容
JEST_CONFIG = '''module.exports = {
  testEnvironment: 'jsdom',
  moduleFileExtensions: ['js', 'json', 'vue'],
  transform: {
    '^.+\\\\.vue$': '@vue/vue3-jest',
    '^.+\\\\.js$': 'babel-jest'
  },
  testMatch: [
    '**/tests/frontend/**/*.test.js',
    '**/tests/frontend/**/*.spec.js'
  ],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  collectCoverageFrom: [
    'src/**/*.{js,vue}',
    '!src/main.js',
    '!src/router/index.js'
  ],
  setupFilesAfterEnv: ['<rootDir>/tests/frontend/setup.js']
}'''

# 测试工具函数示例
TEST_UTILS_EXAMPLE = '''// tests/frontend/utils/test-utils.js
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'

export function createMockRouter(routes = []) {
  return createRouter({
    history: createWebHistory(),
    routes
  })
}

export function mountComponent(component, options = {}) {
  return mount(component, {
    global: {
      plugins: [createMockRouter()]
    },
    ...options
  })
}'''

print("📝 前端测试配置文件说明")
print("="*50)
print()
print("要启用前端测试，需要以下步骤：")
print()
print("1. 安装测试依赖：")
print("   npm install --save-dev @vue/test-utils jest @vue/vue3-jest babel-jest jest-environment-jsdom")
print()
print("2. 创建 jest.config.js 配置文件")
print("3. 在 package.json 中添加测试脚本")
print("4. 创建测试工具函数")
print()
print("💡 这个文件提供了配置模板，可以参考实现完整的前端测试环境")
