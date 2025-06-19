using Newtonsoft.Json;
using RabbitMQ.Client;
using System.Text;

namespace auth_services.Messaging
{
    public class RabbitMQPublisher : IRabbitMQPublisher
    {
        private readonly IConfiguration _config;

        public RabbitMQPublisher(IConfiguration config)
        {
            _config = config;
        }

        public async Task PublishAsync<T>(T message, string _queue)
        {
            var factory = new ConnectionFactory
            {
                HostName = _config["RabbitMQ:Host"],
                Port = int.Parse(_config["RabbitMQ:Port"]),
                UserName = _config["RabbitMQ:Username"],
                Password = _config["RabbitMQ:Password"],
                VirtualHost = _config["RabbitMQ:VirtualHost"]
            };

            await using var connection = await factory.CreateConnectionAsync();
            await using var channel = await connection.CreateChannelAsync();

            await channel.QueueDeclareAsync(
                queue: _queue,
                durable: true,
                exclusive: false,
                autoDelete: false,
                arguments: null);

            var body = Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(message));
            var properties = new BasicProperties { Persistent = true };

            await channel.BasicPublishAsync(
                exchange: "",
                routingKey: _queue,
                mandatory: false,
                basicProperties: properties,
                body: body);
        }
    }
}
