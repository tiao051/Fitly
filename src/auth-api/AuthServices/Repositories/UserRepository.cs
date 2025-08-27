using AuthServices.Data;
using AuthServices.Models;
using Microsoft.EntityFrameworkCore;

namespace AuthServices.Repositories
{
    public class UserRepository : IUserRepository
    {
        private readonly AppDbContext _db;
        public UserRepository(AppDbContext db) => _db = db;

        public Task<User?> GetByEmailAsync(string email) =>
            _db.Users.FirstOrDefaultAsync(u => u.Email == email);

        public async Task AddAsync(User user)
        {
            await _db.Users.AddAsync(user);
            await _db.SaveChangesAsync();
        }
    }
}
