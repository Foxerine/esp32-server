# Java管理API架构文档

## 概述

Java管理API是小智ESP32服务器的管理后台服务，基于Spring Boot框架构建，提供设备管理、用户管理、配置管理、系统监控等RESTful API接口。

## 技术栈

- **Spring Boot**: 2.x (主框架)
- **Spring Security**: 安全认证
- **MyBatis**: 数据持久化
- **MySQL**: 数据库
- **Redis**: 缓存
- **Swagger**: API文档
- **Lombok**: 代码简化

## 项目结构

```
manager-api/
├── src/main/java/xiaozhi/
│   ├── AdminApplication.java          # 启动类
│   ├── common/                        # 公共组件
│   │   ├── annotation/               # 自定义注解
│   │   ├── aspect/                   # AOP切面
│   │   ├── config/                   # 配置类
│   │   ├── constant/                 # 常量定义
│   │   ├── convert/                  # 数据转换
│   │   ├── dao/                      # 数据访问
│   │   ├── entity/                   # 实体类
│   │   ├── exception/                # 异常处理
│   │   ├── handler/                  # 处理器
│   │   ├── interceptor/              # 拦截器
│   │   ├── page/                     # 分页
│   │   ├── redis/                    # Redis操作
│   │   ├── service/                  # 服务层
│   │   ├── user/                     # 用户相关
│   │   ├── utils/                    # 工具类
│   │   ├── validator/                # 验证器
│   │   └── xss/                      # XSS防护
│   └── modules/                      # 业务模块
│       ├── agent/                    # 代理管理
│       ├── config/                   # 配置管理
│       ├── device/                   # 设备管理
│       ├── model/                    # 模型管理
│       ├── security/                 # 安全管理
│       ├── sms/                      # 短信服务
│       ├── sys/                      # 系统管理
│       └── timbre/                   # 音色管理
└── src/main/resources/
    ├── application.yml               # 主配置文件
    ├── application-dev.yml           # 开发环境配置
    ├── db/                          # 数据库脚本
    ├── i18n/                        # 国际化
    ├── logback-spring.xml           # 日志配置
    └── mapper/                      # MyBatis映射文件
```

## 核心架构

### 1. 分层架构

```
Controller Layer (控制器层)
    ↓
Service Layer (服务层)
    ↓
DAO Layer (数据访问层)
    ↓
Database (数据库)
```

### 2. 模块化设计

每个业务模块包含：
- Controller: REST API接口
- Service: 业务逻辑
- DAO: 数据访问
- Entity: 实体类
- DTO: 数据传输对象

## 配置管理

### 1. 主配置文件

```yaml
# application.yml
server:
  port: 8002
  servlet:
    context-path: /xiaozhi

spring:
  profiles:
    active: dev
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://localhost:3306/xiaozhi?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai
    username: root
    password: password
  redis:
    host: localhost
    port: 6379
    database: 0
  jackson:
    date-format: yyyy-MM-dd HH:mm:ss
    time-zone: GMT+8

mybatis:
  mapper-locations: classpath:mapper/**/*.xml
  type-aliases-package: xiaozhi.common.entity
  configuration:
    map-underscore-to-camel-case: true

logging:
  level:
    xiaozhi: debug
```

### 2. 开发环境配置

```yaml
# application-dev.yml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/xiaozhi_dev
    username: dev_user
    password: dev_password

logging:
  level:
    xiaozhi: debug
    org.springframework.web: debug
```

## 安全认证

### 1. JWT认证

```java
// common/config/SecurityConfig.java
@Configuration
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {
    
    @Autowired
    private JwtAuthenticationFilter jwtAuthFilter;
    
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http.csrf().disable()
            .authorizeRequests()
            .antMatchers("/api/auth/**").permitAll()
            .antMatchers("/api/**").authenticated()
            .and()
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);
    }
}
```

### 2. JWT工具类

```java
// common/utils/JwtUtils.java
@Component
public class JwtUtils {
    
    @Value("${jwt.secret}")
    private String secret;
    
    @Value("${jwt.expiration}")
    private Long expiration;
    
    public String generateToken(String username) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + expiration);
        
        return Jwts.builder()
                .setSubject(username)
                .setIssuedAt(now)
                .setExpiration(expiryDate)
                .signWith(SignatureAlgorithm.HS512, secret)
                .compact();
    }
    
    public String getUsernameFromToken(String token) {
        Claims claims = Jwts.parser()
                .setSigningKey(secret)
                .parseClaimsJws(token)
                .getBody();
        
        return claims.getSubject();
    }
    
    public boolean validateToken(String token) {
        try {
            Jwts.parser().setSigningKey(secret).parseClaimsJws(token);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}
```

## 统一响应处理

### 1. 响应结果封装

```java
// common/utils/Result.java
@Data
@AllArgsConstructor
@NoArgsConstructor
public class Result<T> {
    private Integer code;
    private String message;
    private T data;
    
    public static <T> Result<T> success(T data) {
        return new Result<>(200, "success", data);
    }
    
    public static <T> Result<T> error(String message) {
        return new Result<>(500, message, null);
    }
    
    public static <T> Result<T> error(Integer code, String message) {
        return new Result<>(code, message, null);
    }
}
```

### 2. 全局异常处理

```java
// common/handler/GlobalExceptionHandler.java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<Result<String>> handleException(Exception e) {
        log.error("Unexpected error", e);
        return ResponseEntity.ok(Result.error("Internal server error"));
    }
    
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<Result<String>> handleBusinessException(BusinessException e) {
        log.error("Business error: {}", e.getMessage());
        return ResponseEntity.ok(Result.error(e.getCode(), e.getMessage()));
    }
    
    @ExceptionHandler(ValidationException.class)
    public ResponseEntity<Result<String>> handleValidationException(ValidationException e) {
        log.error("Validation error: {}", e.getMessage());
        return ResponseEntity.ok(Result.error(400, e.getMessage()));
    }
}
```

## 业务模块

### 1. 设备管理模块

```java
// modules/device/controller/DeviceController.java
@RestController
@RequestMapping("/api/v1/device")
@Api(tags = "设备管理")
@Slf4j
public class DeviceController {
    
    @Autowired
    private DeviceService deviceService;
    
    @GetMapping
    @ApiOperation("获取设备列表")
    public ResponseEntity<Result<PageResult<DeviceDTO>>> getDeviceList(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer size,
            @RequestParam(required = false) String deviceName) {
        
        PageResult<DeviceDTO> result = deviceService.getDeviceList(page, size, deviceName);
        return ResponseEntity.ok(Result.success(result));
    }
    
    @PostMapping
    @ApiOperation("创建设备")
    public ResponseEntity<Result<DeviceDTO>> createDevice(@RequestBody @Valid DeviceCreateRequest request) {
        DeviceDTO result = deviceService.createDevice(request);
        return ResponseEntity.ok(Result.success(result));
    }
    
    @PutMapping("/{id}")
    @ApiOperation("更新设备")
    public ResponseEntity<Result<DeviceDTO>> updateDevice(
            @PathVariable Long id,
            @RequestBody @Valid DeviceUpdateRequest request) {
        
        DeviceDTO result = deviceService.updateDevice(id, request);
        return ResponseEntity.ok(Result.success(result));
    }
    
    @DeleteMapping("/{id}")
    @ApiOperation("删除设备")
    public ResponseEntity<Result<Void>> deleteDevice(@PathVariable Long id) {
        deviceService.deleteDevice(id);
        return ResponseEntity.ok(Result.success(null));
    }
}
```

### 2. 设备服务层

```java
// modules/device/service/DeviceService.java
@Service
@Slf4j
public class DeviceService {
    
    @Autowired
    private DeviceMapper deviceMapper;
    
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;
    
    public PageResult<DeviceDTO> getDeviceList(Integer page, Integer size, String deviceName) {
        // 构建查询条件
        DeviceQuery query = new DeviceQuery();
        query.setPage(page);
        query.setSize(size);
        query.setDeviceName(deviceName);
        
        // 查询数据
        List<Device> devices = deviceMapper.selectByQuery(query);
        Long total = deviceMapper.countByQuery(query);
        
        // 转换为DTO
        List<DeviceDTO> deviceDTOs = devices.stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
        
        return new PageResult<>(deviceDTOs, total, page, size);
    }
    
    @Transactional
    public DeviceDTO createDevice(DeviceCreateRequest request) {
        // 验证设备名称唯一性
        if (deviceMapper.existsByDeviceName(request.getDeviceName())) {
            throw new BusinessException("设备名称已存在");
        }
        
        // 创建设备实体
        Device device = new Device();
        BeanUtils.copyProperties(request, device);
        device.setCreateTime(new Date());
        device.setStatus(DeviceStatus.ONLINE);
        
        // 保存到数据库
        deviceMapper.insert(device);
        
        // 清除缓存
        redisTemplate.delete("device:list");
        
        return convertToDTO(device);
    }
    
    @Transactional
    public DeviceDTO updateDevice(Long id, DeviceUpdateRequest request) {
        // 查询设备
        Device device = deviceMapper.selectById(id);
        if (device == null) {
            throw new BusinessException("设备不存在");
        }
        
        // 更新设备信息
        BeanUtils.copyProperties(request, device);
        device.setUpdateTime(new Date());
        
        deviceMapper.updateById(device);
        
        // 清除缓存
        redisTemplate.delete("device:list");
        redisTemplate.delete("device:" + id);
        
        return convertToDTO(device);
    }
    
    @Transactional
    public void deleteDevice(Long id) {
        Device device = deviceMapper.selectById(id);
        if (device == null) {
            throw new BusinessException("设备不存在");
        }
        
        deviceMapper.deleteById(id);
        
        // 清除缓存
        redisTemplate.delete("device:list");
        redisTemplate.delete("device:" + id);
    }
    
    private DeviceDTO convertToDTO(Device device) {
        DeviceDTO dto = new DeviceDTO();
        BeanUtils.copyProperties(device, dto);
        return dto;
    }
}
```

### 3. 数据访问层

```java
// modules/device/dao/DeviceMapper.java
@Mapper
public interface DeviceMapper {
    
    List<Device> selectByQuery(DeviceQuery query);
    
    Long countByQuery(DeviceQuery query);
    
    Device selectById(Long id);
    
    int insert(Device device);
    
    int updateById(Device device);
    
    int deleteById(Long id);
    
    boolean existsByDeviceName(String deviceName);
}
```

### 4. MyBatis映射文件

```xml
<!-- mapper/device/DeviceMapper.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="xiaozhi.modules.device.dao.DeviceMapper">
    
    <resultMap id="BaseResultMap" type="xiaozhi.modules.device.entity.Device">
        <id column="id" property="id" jdbcType="BIGINT"/>
        <result column="device_name" property="deviceName" jdbcType="VARCHAR"/>
        <result column="device_type" property="deviceType" jdbcType="VARCHAR"/>
        <result column="status" property="status" jdbcType="VARCHAR"/>
        <result column="create_time" property="createTime" jdbcType="TIMESTAMP"/>
        <result column="update_time" property="updateTime" jdbcType="TIMESTAMP"/>
    </resultMap>
    
    <sql id="Base_Column_List">
        id, device_name, device_type, status, create_time, update_time
    </sql>
    
    <select id="selectByQuery" resultMap="BaseResultMap">
        SELECT <include refid="Base_Column_List"/>
        FROM device
        <where>
            <if test="deviceName != null and deviceName != ''">
                AND device_name LIKE CONCAT('%', #{deviceName}, '%')
            </if>
        </where>
        ORDER BY create_time DESC
        LIMIT #{offset}, #{size}
    </select>
    
    <select id="countByQuery" resultType="long">
        SELECT COUNT(*)
        FROM device
        <where>
            <if test="deviceName != null and deviceName != ''">
                AND device_name LIKE CONCAT('%', #{deviceName}, '%')
            </if>
        </where>
    </select>
    
    <select id="selectById" resultMap="BaseResultMap">
        SELECT <include refid="Base_Column_List"/>
        FROM device
        WHERE id = #{id}
    </select>
    
    <insert id="insert" parameterType="xiaozhi.modules.device.entity.Device" useGeneratedKeys="true" keyProperty="id">
        INSERT INTO device (device_name, device_type, status, create_time)
        VALUES (#{deviceName}, #{deviceType}, #{status}, #{createTime})
    </insert>
    
    <update id="updateById" parameterType="xiaozhi.modules.device.entity.Device">
        UPDATE device
        SET device_name = #{deviceName},
            device_type = #{deviceType},
            status = #{status},
            update_time = #{updateTime}
        WHERE id = #{id}
    </update>
    
    <delete id="deleteById">
        DELETE FROM device WHERE id = #{id}
    </delete>
    
    <select id="existsByDeviceName" resultType="boolean">
        SELECT COUNT(*) > 0
        FROM device
        WHERE device_name = #{deviceName}
    </select>
    
</mapper>
```

## 缓存管理

### 1. Redis配置

```java
// common/config/RedisConfig.java
@Configuration
@EnableCaching
public class RedisConfig {
    
    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory factory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(factory);
        
        // 设置key序列化器
        template.setKeySerializer(new StringRedisSerializer());
        
        // 设置value序列化器
        Jackson2JsonRedisSerializer<Object> serializer = new Jackson2JsonRedisSerializer<>(Object.class);
        ObjectMapper mapper = new ObjectMapper();
        mapper.setVisibility(PropertyAccessor.ALL, JsonAutoDetect.Visibility.ANY);
        mapper.activateDefaultTyping(LaissezFaireSubTypeValidator.instance, ObjectMapper.DefaultTyping.NON_FINAL);
        serializer.setObjectMapper(mapper);
        template.setValueSerializer(serializer);
        
        template.afterPropertiesSet();
        return template;
    }
    
    @Bean
    public CacheManager cacheManager(RedisConnectionFactory factory) {
        RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
                .entryTtl(Duration.ofMinutes(30))
                .serializeKeysWith(RedisSerializationContext.SerializationPair.fromSerializer(new StringRedisSerializer()))
                .serializeValuesWith(RedisSerializationContext.SerializationPair.fromSerializer(new GenericJackson2JsonRedisSerializer()));
        
        return RedisCacheManager.builder(factory)
                .cacheDefaults(config)
                .build();
    }
}
```

### 2. 缓存使用

```java
// 在Service中使用缓存
@Service
public class DeviceService {
    
    @Cacheable(value = "device", key = "#id")
    public DeviceDTO getDeviceById(Long id) {
        Device device = deviceMapper.selectById(id);
        return convertToDTO(device);
    }
    
    @CacheEvict(value = "device", key = "#id")
    public void deleteDevice(Long id) {
        deviceMapper.deleteById(id);
    }
    
    @CachePut(value = "device", key = "#device.id")
    public DeviceDTO updateDevice(Device device) {
        deviceMapper.updateById(device);
        return convertToDTO(device);
    }
}
```

## 国际化支持

### 1. 国际化配置

```java
// common/config/LocaleConfig.java
@Configuration
public class LocaleConfig {
    
    @Bean
    public LocaleResolver localeResolver() {
        SessionLocaleResolver resolver = new SessionLocaleResolver();
        resolver.setDefaultLocale(Locale.SIMPLIFIED_CHINESE);
        return resolver;
    }
    
    @Bean
    public LocaleChangeInterceptor localeChangeInterceptor() {
        LocaleChangeInterceptor interceptor = new LocaleChangeInterceptor();
        interceptor.setParamName("lang");
        return interceptor;
    }
    
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(localeChangeInterceptor());
    }
}
```

### 2. 国际化文件

```properties
# messages_zh_CN.properties
device.create.success=设备创建成功
device.update.success=设备更新成功
device.delete.success=设备删除成功
device.not.found=设备不存在
device.name.exists=设备名称已存在

# messages_en_US.properties
device.create.success=Device created successfully
device.update.success=Device updated successfully
device.delete.success=Device deleted successfully
device.not.found=Device not found
device.name.exists=Device name already exists
```

## 日志配置

### 1. Logback配置

```xml
<!-- logback-spring.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <property name="LOG_PATH" value="logs"/>
    <property name="LOG_PATTERN" value="%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n"/>
    
    <!-- 控制台输出 -->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>${LOG_PATTERN}</pattern>
        </encoder>
    </appender>
    
    <!-- 文件输出 -->
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_PATH}/xiaozhi-api.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>${LOG_PATH}/xiaozhi-api.%d{yyyy-MM-dd}.%i.log</fileNamePattern>
            <timeBasedFileNamingAndTriggeringPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedFNATP">
                <maxFileSize>100MB</maxFileSize>
            </timeBasedFileNamingAndTriggeringPolicy>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
        <encoder>
            <pattern>${LOG_PATTERN}</pattern>
        </encoder>
    </appender>
    
    <!-- 错误日志 -->
    <appender name="ERROR_FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_PATH}/xiaozhi-api-error.log</file>
        <filter class="ch.qos.logback.classic.filter.LevelFilter">
            <level>ERROR</level>
            <onMatch>ACCEPT</onMatch>
            <onMismatch>DENY</onMismatch>
        </filter>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>${LOG_PATH}/xiaozhi-api-error.%d{yyyy-MM-dd}.%i.log</fileNamePattern>
            <timeBasedFileNamingAndTriggeringPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedFNATP">
                <maxFileSize>100MB</maxFileSize>
            </timeBasedFileNamingAndTriggeringPolicy>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
        <encoder>
            <pattern>${LOG_PATTERN}</pattern>
        </encoder>
    </appender>
    
    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="FILE"/>
        <appender-ref ref="ERROR_FILE"/>
    </root>
    
    <logger name="xiaozhi" level="DEBUG"/>
    <logger name="org.springframework.web" level="INFO"/>
    <logger name="org.mybatis" level="INFO"/>
</configuration>
```

## 扩展开发指南

### 1. 添加新的业务模块

1. 创建模块目录结构
2. 实现Controller、Service、DAO层
3. 创建实体类和DTO
4. 编写MyBatis映射文件
5. 添加单元测试

### 2. 添加新的API接口

```java
@RestController
@RequestMapping("/api/v1/example")
@Api(tags = "示例管理")
public class ExampleController {
    
    @Autowired
    private ExampleService exampleService;
    
    @GetMapping("/{id}")
    @ApiOperation("获取示例详情")
    public ResponseEntity<Result<ExampleDTO>> getExample(@PathVariable Long id) {
        ExampleDTO result = exampleService.getById(id);
        return ResponseEntity.ok(Result.success(result));
    }
    
    @PostMapping
    @ApiOperation("创建示例")
    public ResponseEntity<Result<ExampleDTO>> createExample(@RequestBody @Valid ExampleCreateRequest request) {
        ExampleDTO result = exampleService.create(request);
        return ResponseEntity.ok(Result.success(result));
    }
}
```

### 3. 添加自定义注解

```java
// common/annotation/Log.java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface Log {
    String value() default "";
    String module() default "";
}
```

### 4. 添加AOP切面

```java
// common/aspect/LogAspect.java
@Aspect
@Component
@Slf4j
public class LogAspect {
    
    @Around("@annotation(logAnnotation)")
    public Object around(ProceedingJoinPoint point, Log logAnnotation) throws Throwable {
        long startTime = System.currentTimeMillis();
        
        try {
            Object result = point.proceed();
            long endTime = System.currentTimeMillis();
            
            log.info("Method: {}, Module: {}, Duration: {}ms", 
                    point.getSignature().getName(),
                    logAnnotation.module(),
                    endTime - startTime);
            
            return result;
        } catch (Exception e) {
            log.error("Method execution error: {}", e.getMessage(), e);
            throw e;
        }
    }
}
```

## 测试策略

### 1. 单元测试

```java
// src/test/java/xiaozhi/modules/device/DeviceServiceTest.java
@SpringBootTest
class DeviceServiceTest {
    
    @Autowired
    private DeviceService deviceService;
    
    @MockBean
    private DeviceMapper deviceMapper;
    
    @Test
    void testCreateDevice() {
        // 准备测试数据
        DeviceCreateRequest request = new DeviceCreateRequest();
        request.setDeviceName("测试设备");
        request.setDeviceType("ESP32");
        
        Device device = new Device();
        device.setId(1L);
        device.setDeviceName("测试设备");
        device.setDeviceType("ESP32");
        
        // Mock方法调用
        when(deviceMapper.existsByDeviceName("测试设备")).thenReturn(false);
        when(deviceMapper.insert(any(Device.class))).thenReturn(1);
        
        // 执行测试
        DeviceDTO result = deviceService.createDevice(request);
        
        // 验证结果
        assertNotNull(result);
        assertEquals("测试设备", result.getDeviceName());
        assertEquals("ESP32", result.getDeviceType());
    }
}
```

### 2. 集成测试

```java
// src/test/java/xiaozhi/modules/device/DeviceControllerTest.java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class DeviceControllerTest {
    
    @Autowired
    private TestRestTemplate restTemplate;
    
    @Test
    void testGetDeviceList() {
        // 执行测试
        ResponseEntity<Result> response = restTemplate.getForEntity(
                "/api/v1/device?page=1&size=10", Result.class);
        
        // 验证结果
        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertNotNull(response.getBody());
        assertEquals(200, response.getBody().getCode());
    }
}
```

## 部署配置

### 1. 生产环境配置

```yaml
# application-prod.yml
spring:
  datasource:
    url: jdbc:mysql://prod-db:3306/xiaozhi?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
  redis:
    host: prod-redis
    port: 6379
    password: ${REDIS_PASSWORD}

logging:
  level:
    xiaozhi: INFO
    org.springframework.web: WARN
```

### 2. Docker配置

```dockerfile
# Dockerfile
FROM openjdk:8-jre-alpine

WORKDIR /app

COPY target/manager-api.jar app.jar

EXPOSE 8002

CMD ["java", "-jar", "app.jar"]
```

### 3. 系统服务配置

```ini
# /etc/systemd/system/xiaozhi-api.service
[Unit]
Description=Xiaozhi Java API
After=network.target

[Service]
Type=simple
User=xiaozhi
WorkingDirectory=/opt/xiaozhi-api
ExecStart=/usr/bin/java -jar manager-api.jar --spring.profiles.active=prod
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 性能优化

### 1. 数据库优化

- 使用连接池
- 优化SQL查询
- 添加索引
- 使用读写分离

### 2. 缓存优化

- 合理使用Redis缓存
- 设置合适的缓存过期时间
- 使用缓存预热

### 3. JVM优化

```bash
# JVM参数优化
java -Xms2g -Xmx4g -XX:+UseG1GC -XX:MaxGCPauseMillis=200 -jar app.jar
```

## 监控和运维

### 1. 健康检查

```java
// 添加健康检查端点
@RestController
public class HealthController {
    
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> health = new HashMap<>();
        health.put("status", "UP");
        health.put("timestamp", new Date());
        return ResponseEntity.ok(health);
    }
}
```

### 2. 性能监控

- 使用Spring Boot Actuator
- 集成Micrometer监控
- 添加自定义指标

## 总结

Java管理API采用Spring Boot框架，实现了模块化、分层化的架构设计，提供了完整的设备管理、用户管理等功能。通过合理的配置管理、安全认证、缓存策略和测试覆盖，确保系统的稳定性和可维护性。 