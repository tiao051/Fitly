using body_analysis_ai_services.DTOs;
using Microsoft.AspNetCore.Mvc;

namespace body_analysis_ai_services.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class BodyAnalyze : ControllerBase
    {
        [HttpPost("analyze")]
        public async Task<IActionResult> Analyze([FromBody] AnalyzeRequest request)
        {
            if (string.IsNullOrEmpty(request.UrlImg))
            {
                return BadRequest("Image URL cannot be null or empty.");
            }

            // TODO: Gọi service xử lý AI tại đây. Tạm thời mock kết quả.
            var result = new AnalyzeResult
            {
                Status = "Success",
                BodyType = "V-Taper",
                Confidence = 0.92
            };

            // Simulate delay
            await Task.Delay(300);

            return Ok(result);
        }
    }
}
