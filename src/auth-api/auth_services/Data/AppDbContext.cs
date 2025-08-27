
using auth_services.Models;
using Microsoft.EntityFrameworkCore;

namespace auth_services.Data
{
    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }
        public DbSet<User> Users => Set<User>();
    }
}
