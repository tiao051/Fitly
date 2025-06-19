namespace auth_services.Messaging
{
    public interface IRabbitMQPublisher
    {
        Task PublishAsync<T>(T message, string _queue);
    }
}
